from sqlalchemy.orm import Session
from fastapi import HTTPException
from ..models import Pipeline, CVOperation
from datetime import datetime
from typing import List, Optional, Dict, Any, Union, Tuple
import json
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
from enum import Enum

class NodeType(Enum):
    START = 'start'
    END = 'end'
    OPERATION = 'operation'
    CONDITION = 'condition'
    MERGE = 'merge'

class EdgeType(Enum):
    NORMAL = 'normal'
    TRUE = 'true'
    FALSE = 'false'

class NodeResult:
    def __init__(self, 
                 node_type: NodeType,
                 success: bool = True,
                 result: Any = None,
                 error: str = None,
                 operation_id: int = None,
                 operation_name: str = None,
                 output_type: str = None):
        self.node_type = node_type
        self.success = success
        self.result = result
        self.error = error
        self.operation_id = operation_id
        self.operation_name = operation_name
        self.output_type = output_type

    def to_dict(self) -> dict:
        return {
            'type': self.node_type.value,
            'success': self.success,
            'result': self.result,
            'error': self.error,
            'operation_id': self.operation_id,
            'operation_name': self.operation_name,
            'output_type': self.output_type
        }

class PipelineService:
    def __init__(self, db: Session):
        self.db = db

    def get_pipelines(self) -> List[Pipeline]:
        """获取所有管道"""
        return self.db.query(Pipeline).all()

    def get_pipeline(self, pipeline_id: int) -> Optional[Pipeline]:
        """获取指定管道"""
        return self.db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    def create_pipeline(self, name: str, description: str = None, operations: list = None) -> Pipeline:
        """创建新的管道"""
        try:
            pipeline = Pipeline(
                name=name,
                description=description,
                operations=operations or [],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(pipeline)
            self.db.commit()
            self.db.refresh(pipeline)
            return pipeline
        except Exception as e:
            self.db.rollback()
            raise e

    def update_pipeline(self, pipeline_id: int, name: str = None, 
                       description: str = None, operations: list = None) -> Pipeline:
        """更新管道"""
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")

        if name is not None:
            pipeline.name = name
        if description is not None:
            pipeline.description = description
        if operations is not None:
            pipeline.operations = operations
            
        pipeline.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(pipeline)
            return pipeline
        except Exception as e:
            self.db.rollback()
            raise e

    def delete_pipeline(self, pipeline_id: int) -> None:
        """删除管道"""
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")
            
        try:
            self.db.delete(pipeline)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def _execute_operation(self, operation: CVOperation, img: np.ndarray) -> dict:
        """执行单个操作"""
        try:
            namespace = {}
            exec(operation.code, namespace)
            result = namespace['process'](img, cv2, np)

            return {
                'operation_id': operation.id,
                'operation_name': operation.name,
                'output_type': operation.output_type,
                'result': result,
                'success': True
            }
        except Exception as e:
            return {
                'operation_id': operation.id,
                'operation_name': operation.name,
                'output_type': operation.output_type,
                'error': str(e),
                'success': False
            }

    def _process_node(self, node_id: str, nodes: Dict[str, Any], 
                     edges: List[Dict[str, str]], operations: Dict[int, CVOperation], 
                     results: Dict[str, NodeResult], img: np.ndarray) -> Tuple[bool, Optional[np.ndarray]]:
        """处理单个节点，返回(是否继续执行, 输出图像)"""
        node = nodes[node_id]
        node_type = NodeType(node.get('type', NodeType.OPERATION.value))
        
        # 处理开始节点
        if node_type == NodeType.START:
            results[node_id] = NodeResult(
                node_type=NodeType.START,
                output_type='image',
                result=img
            )
            return True, img
        
        # 处理结束节点
        if node_type == NodeType.END:
            results[node_id] = NodeResult(node_type=NodeType.END)
            return True, img

        # 处理条件节点
        if node_type == NodeType.CONDITION:
            condition_result = self._evaluate_condition(node, results)
            results[node_id] = NodeResult(
                node_type=NodeType.CONDITION,
                result=condition_result
            )
            return condition_result, img

        # 处理合并节点
        if node_type == NodeType.MERGE:
            input_edges = [edge for edge in edges if edge['target'] == node_id]
            input_results = [results[edge['source']] for edge in input_edges]
            
            # 合并结果
            merged_result = self._merge_results(input_results)
            results[node_id] = NodeResult(
                node_type=NodeType.MERGE,
                result=merged_result
            )
            return True, img

        # 处理操作节点
        operation_id = node.get('operation_id')
        if operation_id:
            operation = operations.get(operation_id)
            if not operation:
                raise HTTPException(status_code=404, detail=f"Operation {operation_id} not found")

            # 执行操作
            try:
                namespace = {}
                exec(operation.code, namespace)
                result = namespace['process'](img, cv2, np)

                results[node_id] = NodeResult(
                    node_type=NodeType.OPERATION,
                    operation_id=operation.id,
                    operation_name=operation.name,
                    output_type=operation.output_type,
                    result=result
                )
                
                return True, result if operation.output_type == 'image' else img
                
            except Exception as e:
                results[node_id] = NodeResult(
                    node_type=NodeType.OPERATION,
                    success=False,
                    error=str(e),
                    operation_id=operation.id,
                    operation_name=operation.name,
                    output_type=operation.output_type
                )
                raise HTTPException(
                    status_code=400,
                    detail=f"Error in operation {operation.name}: {str(e)}"
                )

        return True, img

    def _evaluate_condition(self, node: Dict[str, Any], results: Dict[str, NodeResult]) -> bool:
        """评估条件节点"""
        condition = node.get('condition', {})
        condition_type = condition.get('type')
        
        if condition_type == 'compare':
            value = condition.get('value')
            operator = condition.get('operator', '==')
            source_node = condition.get('source_node')
            
            if source_node and source_node in results:
                source_result = results[source_node].result
                
                try:
                    if operator == '==':
                        return source_result == value
                    elif operator == '!=':
                        return source_result != value
                    elif operator == '>':
                        return float(source_result) > float(value)
                    elif operator == '<':
                        return float(source_result) < float(value)
                    elif operator == '>=':
                        return float(source_result) >= float(value)
                    elif operator == '<=':
                        return float(source_result) <= float(value)
                except (ValueError, TypeError) as e:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid comparison: {str(e)}"
                    )
        
        elif condition_type == 'and':
            conditions = condition.get('conditions', [])
            return all(self._evaluate_condition({'condition': c}, results) for c in conditions)
        
        elif condition_type == 'or':
            conditions = condition.get('conditions', [])
            return any(self._evaluate_condition({'condition': c}, results) for c in conditions)
        
        elif condition_type == 'not':
            subcondition = condition.get('condition', {})
            return not self._evaluate_condition({'condition': subcondition}, results)
                
        return False

    def _merge_results(self, results: List[NodeResult]) -> Any:
        """合并多个节点的结果"""
        # 如果只有一个结果，直接返回
        if len(results) == 1:
            return results[0].result
        
        # 如果有图像结果，优先返回最后一个图像
        image_results = [r for r in results if r.output_type == 'image']
        if image_results:
            return image_results[-1].result
        
        # 否则返回所有结果的列表
        return [r.result for r in results]

    def apply_pipeline(self, image_data: bytes, pipeline_id: int) -> dict:
        """应用管道处理"""
        pipeline = self.get_pipeline(pipeline_id)
        if not pipeline:
            raise HTTPException(status_code=404, detail="Pipeline not found")

        try:
            # 解析配置
            config = pipeline.operations
            nodes = {node['id']: node for node in config.get('nodes', [])}
            edges = config.get('edges', [])

            # 验证管道配置
            self._validate_pipeline_config(nodes, edges)

            # 获取操作列表
            operation_ids = [
                node['operation_id'] 
                for node in nodes.values() 
                if node.get('type') == NodeType.OPERATION.value and 'operation_id' in node
            ]
            operations = {
                op.id: op for op in 
                self.db.query(CVOperation).filter(CVOperation.id.in_(operation_ids)).all()
            }

            # 准备图像数据
            img = self._prepare_image(image_data)

            # 执行管道
            results = self._execute_pipeline(nodes, edges, operations, img)

            # 处理最终结果
            return self._process_final_results(results)

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error processing image: {str(e)}"
            )

    def _validate_pipeline_config(self, nodes: Dict[str, Any], edges: List[Dict[str, str]]) -> None:
        """验证管道配置的有效性"""
        # 检查是否有开始和结束节点
        start_nodes = [n for n in nodes.values() if n.get('type') == NodeType.START.value]
        end_nodes = [n for n in nodes.values() if n.get('type') == NodeType.END.value]
        
        if not start_nodes:
            raise HTTPException(status_code=400, detail="Pipeline must have a start node")
        if len(start_nodes) > 1:
            raise HTTPException(status_code=400, detail="Pipeline can only have one start node")
        if not end_nodes:
            raise HTTPException(status_code=400, detail="Pipeline must have at least one end node")

        # 获取开始节点的ID
        start_node_id = start_nodes[0]['id']
        
        # 检查开始节点的输入边
        start_input_edges = [edge for edge in edges if edge['target'] == start_node_id]
        if start_input_edges:
            raise HTTPException(
                status_code=400, 
                detail="Start node cannot have input edges"
            )

        # 检查边的有效性
        for edge in edges:
            if edge['source'] not in nodes:
                raise HTTPException(status_code=400, detail=f"Invalid edge source: {edge['source']}")
            if edge['target'] not in nodes:
                raise HTTPException(status_code=400, detail=f"Invalid edge target: {edge['target']}")
            
            # 检查边的类型
            source_type = nodes[edge['source']].get('type')
            target_type = nodes[edge['target']].get('type')
            
            # 条件节点的输出边必须标记为true/false
            if source_type == NodeType.CONDITION.value:
                edge_type = edge.get('type', EdgeType.NORMAL.value)
                if edge_type not in [EdgeType.TRUE.value, EdgeType.FALSE.value]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Condition node edges must be marked as 'true' or 'false'"
                    )

        # 检查是否有环
        if self._has_cycle(nodes, edges):
            raise HTTPException(status_code=400, detail="Pipeline contains cycles")

        # 构建邻接表
        adj_list = {node_id: [] for node_id in nodes}
        for edge in edges:
            adj_list[edge['source']].append(edge['target'])

        # 获取开始和结束节点
        start_nodes = [n['id'] for n in nodes.values() if n.get('type') == NodeType.START.value]
        end_nodes = [n['id'] for n in nodes.values() if n.get('type') == NodeType.END.value]
        
        # 验证从开始节点到结束节点的可达性
        def can_reach_end(start: str, visited: set) -> bool:
            if start in end_nodes:
                return True
            
            visited.add(start)
            for next_node in adj_list[start]:
                if next_node not in visited and can_reach_end(next_node, visited):
                    return True
            return False

        # 检查从开始节点是否可以到达任意结束节点
        if not can_reach_end(start_nodes[0], set()):
            raise HTTPException(
                status_code=400,
                detail="Start node must have a path to at least one end node"
            )

        # 检查所有节点的出度
        out_degrees = {node_id: 0 for node_id in nodes}
        for edge in edges:
            out_degrees[edge['source']] += 1

        # 验证结束节点没有出边
        for end_node in end_nodes:
            if out_degrees[end_node] > 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"End node {end_node} cannot have outgoing edges"
                )

        # 验证非结束节点都有出边（除了结束节点）
        for node_id, degree in out_degrees.items():
            if degree == 0 and node_id not in end_nodes:
                raise HTTPException(
                    status_code=400,
                    detail=f"Non-end node {node_id} must have at least one outgoing edge"
                )

        # 验证条件节点有且仅有两个出边（true和false分支）
        for node_id, node in nodes.items():
            if node.get('type') == NodeType.CONDITION.value:
                outgoing_edges = [e for e in edges if e['source'] == node_id]
                true_edges = [e for e in outgoing_edges if e.get('type') == EdgeType.TRUE.value]
                false_edges = [e for e in outgoing_edges if e.get('type') == EdgeType.FALSE.value]
                
                if len(true_edges) != 1 or len(false_edges) != 1:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Condition node {node_id} must have exactly one 'true' and one 'false' edge"
                    )

        # 验证合并节点至少有两个入边
        for node_id, node in nodes.items():
            if node.get('type') == NodeType.MERGE.value:
                incoming_edges = [e for e in edges if e['target'] == node_id]
                if len(incoming_edges) < 2:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Merge node {node_id} must have at least two incoming edges"
                    )

        # 计算所有节点的入度和出度
        in_degrees = {node_id: 0 for node_id in nodes}
        out_degrees = {node_id: 0 for node_id in nodes}
        for edge in edges:
            out_degrees[edge['source']] += 1
            in_degrees[edge['target']] += 1

        # 验证操作节点的入度和出度
        for node_id, node in nodes.items():
            if node.get('type') == NodeType.OPERATION.value:
                # 验证入度
                if in_degrees[node_id] != 1:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Operation node {node_id} must have exactly one input edge (found {in_degrees[node_id]})"
                    )
                
                # 验证出度
                if out_degrees[node_id] != 1:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Operation node {node_id} must have exactly one output edge (found {out_degrees[node_id]})"
                    )

                # 验证输入边的类型
                input_edges = [e for e in edges if e['target'] == node_id]
                if any(e.get('type') != EdgeType.NORMAL.value for e in input_edges):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Operation node {node_id} can only have normal type input edges"
                    )

                # 验证输出边的类型
                output_edges = [e for e in edges if e['source'] == node_id]
                if any(e.get('type') != EdgeType.NORMAL.value for e in output_edges):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Operation node {node_id} can only have normal type output edges"
                    )

        # 验证节点连接的数据流
        for edge in edges:
            source_node = nodes[edge['source']]
            target_node = nodes[edge['target']]
            source_type = source_node.get('type')
            target_type = target_node.get('type')

            # 验证数据流的合法性
            if source_type == NodeType.OPERATION.value:
                # 操作节点的输出必须匹配下一个节点的输入要求
                operation = self.db.query(CVOperation).filter(
                    CVOperation.id == source_node.get('operation_id')
                ).first()
                
                if not operation:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Operation not found for node {edge['source']}"
                    )

                # 如果目标是操作节点，检查输出类型是否为图像
                if target_type == NodeType.OPERATION.value:
                    if operation.output_type != 'image':
                        raise HTTPException(
                            status_code=400,
                            detail=f"Operation node {edge['source']} must output image to connect to another operation node"
                        )

    def _prepare_image(self, image_data: bytes) -> np.ndarray:
        """准备图像数据"""
        try:
            nparr = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                raise HTTPException(status_code=400, detail="Invalid image file")
            
            return img
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error preparing image: {str(e)}"
            )

    def _execute_pipeline(self, nodes: Dict[str, Any], edges: List[Dict[str, str]], 
                         operations: Dict[int, CVOperation], img: np.ndarray) -> Dict[str, NodeResult]:
        """执行管道处理"""
        results = {}
        node_images = {'start': img}  # 存储每个节点的输出图像
        
        # 构建节点依赖关系
        dependencies = {node_id: [] for node_id in nodes}
        for edge in edges:
            dependencies[edge['target']].append(edge['source'])

        # 使用线程池处理并行节点
        max_workers = min(len(nodes), 4)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while len(results) < len(nodes):
                ready_nodes = [
                    node_id for node_id in nodes
                    if node_id not in results and
                    all(dep in results for dep in dependencies[node_id])
                ]

                if not ready_nodes:
                    if len(results) < len(nodes):
                        raise HTTPException(
                            status_code=400,
                            detail="Pipeline execution deadlock detected"
                        )
                    break

                batch_size = min(len(ready_nodes), max_workers)
                current_batch = ready_nodes[:batch_size]
                
                futures = []
                for node_id in current_batch:
                    # 获取输入图像 - 修改这部分以确保只使用直接前驱节点的输出
                    input_edges = [edge for edge in edges if edge['target'] == node_id]
                    
                    if not input_edges:  # 开始节点
                        node_images[node_id] = img
                    else:
                        # 获取直接前驱节点
                        prev_node_id = input_edges[0]['source']
                        prev_node = nodes[prev_node_id]
                        prev_result = results[prev_node_id]

                        if prev_node.get('type') == NodeType.OPERATION.value:
                            # 如果前驱是操作节点，使用其输出
                            if prev_result.output_type == 'image':
                                node_images[node_id] = prev_result.result
                            else:
                                # 如果不是图像输出，继续使用上一个图像
                                node_images[node_id] = node_images[prev_node_id]
                        else:
                            # 对于非操作节点，继承其输入图像
                            node_images[node_id] = node_images[prev_node_id]

                    futures.append(
                        executor.submit(
                            self._process_node,
                            node_id, nodes, edges, operations,
                            results, node_images[node_id]
                        )
                    )

                # 等待当前批次完成
                for future in as_completed(futures):
                    try:
                        continue_exec, result_img = future.result()
                        if result_img is not None:
                            node_id = current_batch[len(futures) - len(as_completed(futures))]
                            node_images[node_id] = result_img
                    except Exception as e:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Error in pipeline execution: {str(e)}"
                        )

        return results

    def _process_final_results(self, results: Dict[str, NodeResult]) -> dict:
        """处理最终结果"""
        # 找到所有终止节点（没有出边的节点）
        final_results = [
            result for result in results.values()
            if result.node_type == NodeType.END
        ]

        if not final_results:
            raise HTTPException(
                status_code=400,
                detail="No end node results found"
            )

        # 转换结果为可序列化格式
        serialized_results = [result.to_dict() for result in results.values()]
        
        # 获取最后一个图像结果
        image_results = [
            r for r in results.values()
            if r.output_type == 'image' and isinstance(r.result, np.ndarray)
        ]
        
        if image_results:
            last_image = image_results[-1].result
            success, encoded_img = cv2.imencode('.png', last_image)
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to encode final image"
                )
            return {
                'type': 'pipeline',
                'data': encoded_img.tobytes(),
                'results': serialized_results
            }
        
        return {
            'type': 'pipeline',
            'data': None,
            'results': serialized_results
        }

    def _has_cycle(self, nodes: Dict[str, Any], edges: List[Dict[str, str]]) -> bool:
        """检测图中是否存在环"""
        def dfs(node: str, visited: set, path: set) -> bool:
            visited.add(node)
            path.add(node)
            
            # 检查所有出边
            for edge in edges:
                if edge['source'] == node:
                    next_node = edge['target']
                    if next_node in path:
                        return True  # 发现环
                    if next_node not in visited:
                        if dfs(next_node, visited, path):
                            return True
                        
            path.remove(node)
            return False

        visited = set()
        path = set()
        
        # 从每个未访问的节点开始DFS
        for node in nodes:
            if node not in visited:
                if dfs(node, visited, path):
                    return True
                
        return False 