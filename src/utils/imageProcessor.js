/**
 * 图像预处理工具类
 * 提供基础的图像处理功能，包括灰度转换、二值化、降噪等
 */

export class ImageProcessor {
  /**
   * 将图像转换为灰度
   * @param {ImageData} imageData - 原始图像数据
   * @returns {ImageData} 灰度图像数据
   */
  static toGrayscale(imageData) {
    const gray = new ImageData(imageData.width, imageData.height)
    const data = imageData.data
    const grayData = gray.data

    for (let i = 0; i < data.length; i += 4) {
      const r = data[i]
      const g = data[i + 1]
      const b = data[i + 2]
      // 使用BT.601标准的灰度转换公式
      const value = 0.299 * r + 0.587 * g + 0.114 * b
      grayData[i] = value
      grayData[i + 1] = value
      grayData[i + 2] = value
      grayData[i + 3] = data[i + 3] // 保持原始alpha通道
    }

    return gray
  }

  /**
   * 对图像进行二值化处理
   * @param {ImageData} imageData - 灰度图像数据
   * @param {number} threshold - 二值化阈值(0-255)
   * @returns {ImageData} 二值化后的图像数据
   */
  static threshold(imageData, threshold = 128) {
    const binary = new ImageData(imageData.width, imageData.height)
    const data = imageData.data
    const binaryData = binary.data

    for (let i = 0; i < data.length; i += 4) {
      const value = data[i] > threshold ? 255 : 0
      binaryData[i] = value
      binaryData[i + 1] = value
      binaryData[i + 2] = value
      binaryData[i + 3] = data[i + 3]
    }

    return binary
  }

  /**
   * 使用中值滤波进行降噪
   * @param {ImageData} imageData - 原始图像数据
   * @param {number} kernelSize - 滤波核大小(3, 5, 7等奇数)
   * @returns {ImageData} 降噪后的图像数据
   */
  static medianFilter(imageData, kernelSize = 3) {
    const filtered = new ImageData(imageData.width, imageData.height)
    const data = imageData.data
    const filteredData = filtered.data
    const width = imageData.width
    const height = imageData.height
    const halfKernel = Math.floor(kernelSize / 2)

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const values = []

        // 收集核范围内的像素值
        for (let ky = -halfKernel; ky <= halfKernel; ky++) {
          for (let kx = -halfKernel; kx <= halfKernel; kx++) {
            const px = Math.min(Math.max(x + kx, 0), width - 1)
            const py = Math.min(Math.max(y + ky, 0), height - 1)
            const idx = (py * width + px) * 4
            values.push(data[idx])
          }
        }

        // 计算中值
        values.sort((a, b) => a - b)
        const medianValue = values[Math.floor(values.length / 2)]

        // 设置像素值
        const idx = (y * width + x) * 4
        filteredData[idx] = medianValue
        filteredData[idx + 1] = medianValue
        filteredData[idx + 2] = medianValue
        filteredData[idx + 3] = data[idx + 3]
      }
    }

    return filtered
  }

  /**
   * 调整图像对比度
   * @param {ImageData} imageData - 原始图像数据
   * @param {number} contrast - 对比度调整值(-100到100)
   * @returns {ImageData} 调整后的图像数据
   */
  static adjustContrast(imageData, contrast = 0) {
    const adjusted = new ImageData(imageData.width, imageData.height)
    const data = imageData.data
    const adjustedData = adjusted.data
    const factor = (259 * (contrast + 255)) / (255 * (259 - contrast))

    for (let i = 0; i < data.length; i += 4) {
      adjustedData[i] = Math.min(255, Math.max(0, factor * (data[i] - 128) + 128))
      adjustedData[i + 1] = Math.min(255, Math.max(0, factor * (data[i + 1] - 128) + 128))
      adjustedData[i + 2] = Math.min(255, Math.max(0, factor * (data[i + 2] - 128) + 128))
      adjustedData[i + 3] = data[i + 3]
    }

    return adjusted
  }

  /**
   * 检测图像边缘
   * @param {ImageData} imageData - 灰度图像数据
   * @returns {ImageData} 边缘检测后的图像数据
   */
  static detectEdges(imageData) {
    const edges = new ImageData(imageData.width, imageData.height)
    const data = imageData.data
    const edgesData = edges.data
    const width = imageData.width
    const height = imageData.height

    // Sobel算子
    const sobelX = [-1, 0, 1, -2, 0, 2, -1, 0, 1]
    const sobelY = [-1, -2, -1, 0, 0, 0, 1, 2, 1]

    for (let y = 1; y < height - 1; y++) {
      for (let x = 1; x < width - 1; x++) {
        let gx = 0
        let gy = 0

        // 应用Sobel算子
        for (let ky = -1; ky <= 1; ky++) {
          for (let kx = -1; kx <= 1; kx++) {
            const idx = ((y + ky) * width + (x + kx)) * 4
            const value = data[idx]
            gx += value * sobelX[(ky + 1) * 3 + (kx + 1)]
            gy += value * sobelY[(ky + 1) * 3 + (kx + 1)]
          }
        }

        // 计算梯度幅值
        const magnitude = Math.min(255, Math.sqrt(gx * gx + gy * gy))
        const idx = (y * width + x) * 4

        edgesData[idx] = magnitude
        edgesData[idx + 1] = magnitude
        edgesData[idx + 2] = magnitude
        edgesData[idx + 3] = 255
      }
    }

    return edges
  }

  /**
   * 分割图像中的字符区域
   * @param {ImageData} imageData - 二值化后的图像数据
   * @returns {Array<{x: number, y: number, width: number, height: number}>} 字符区域的边界框数组
   */
  static segmentCharacters(imageData) {
    const data = imageData.data
    const width = imageData.width
    const height = imageData.height
    const visited = new Set()
    const characters = []

    // 连通区域标记
    function bfs(startX, startY) {
      const queue = [[startX, startY]]
      const points = [[startX, startY]]
      visited.add(`${startX},${startY}`)

      while (queue.length > 0) {
        const [x, y] = queue.shift()

        // 8邻域搜索
        const neighbors = [
          [x-1, y-1], [x, y-1], [x+1, y-1],
          [x-1, y],            [x+1, y],
          [x-1, y+1], [x, y+1], [x+1, y+1]
        ]

        for (const [nx, ny] of neighbors) {
          if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
            const key = `${nx},${ny}`
            const idx = (ny * width + nx) * 4
            if (data[idx] === 0 && !visited.has(key)) {
              queue.push([nx, ny])
              points.push([nx, ny])
              visited.add(key)
            }
          }
        }
      }

      return points
    }

    // 遍历图像查找字符区域
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const idx = (y * width + x) * 4
        const key = `${x},${y}`
        
        if (data[idx] === 0 && !visited.has(key)) {
          const points = bfs(x, y)
          
          // 计算边界框
          const xs = points.map(p => p[0])
          const ys = points.map(p => p[1])
          const minX = Math.min(...xs)
          const maxX = Math.max(...xs)
          const minY = Math.min(...ys)
          const maxY = Math.max(...ys)
          
          // 过滤掉太小的区域（噪点）
          const area = (maxX - minX + 1) * (maxY - minY + 1)
          if (area > 100) { // 可调整的阈值
            characters.push({
              x: minX,
              y: minY,
              width: maxX - minX + 1,
              height: maxY - minY + 1
            })
          }
        }
      }
    }

    return characters
  }

  /**
   * 提取字符区域的特征
   * @param {ImageData} imageData - 二值化后的图像数据
   * @param {Object} region - 字符区域的边界框
   * @returns {Object} 字符特征
   */
  static extractFeatures(imageData, region) {
    const { x, y, width, height } = region
    const data = imageData.data
    const imgWidth = imageData.width

    // 计算投影特征
    const horizontalProjection = new Array(height).fill(0)
    const verticalProjection = new Array(width).fill(0)

    for (let j = y; j < y + height; j++) {
      for (let i = x; i < x + width; i++) {
        const idx = (j * imgWidth + i) * 4
        if (data[idx] === 0) {
          horizontalProjection[j - y]++
          verticalProjection[i - x]++
        }
      }
    }

    // 计算笔画交叉点数
    let crossPoints = 0
    for (let j = y + 1; j < y + height - 1; j++) {
      for (let i = x + 1; i < x + width - 1; i++) {
        const idx = (j * imgWidth + i) * 4
        if (data[idx] === 0) {
          const neighbors = [
            data[((j-1) * imgWidth + i) * 4],     // 上
            data[((j+1) * imgWidth + i) * 4],     // 下
            data[(j * imgWidth + (i-1)) * 4],     // 左
            data[(j * imgWidth + (i+1)) * 4]      // 右
          ]
          if (neighbors.filter(v => v === 0).length >= 3) {
            crossPoints++
          }
        }
      }
    }

    return {
      horizontalProjection,
      verticalProjection,
      crossPoints,
      aspectRatio: width / height
    }
  }

  /**
   * 计算图像的最佳二值化阈值（使用OTSU算法）
   * @param {ImageData} imageData - 灰度图像数据
   * @returns {number} 最佳阈值
   */
  /**
   * 应用自适应阈值
   * @param {ImageData} imageData - 灰度图像数据
   * @param {number} blockSize - 邻域块大小
   * @param {number} C - 常数偏移值
   * @returns {ImageData} 二值化后的图像数据
   */
  static adaptiveThreshold(imageData, blockSize = 11, C = 2) {
    const width = imageData.width
    const height = imageData.height
    const result = new ImageData(width, height)
    const data = imageData.data
    const resultData = result.data
    const halfBlock = Math.floor(blockSize / 2)

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        let sum = 0
        let count = 0

        // 计算邻域平均值
        for (let dy = -halfBlock; dy <= halfBlock; dy++) {
          for (let dx = -halfBlock; dx <= halfBlock; dx++) {
            const nx = x + dx
            const ny = y + dy
            if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
              sum += data[(ny * width + nx) * 4]
              count++
            }
          }
        }

        const threshold = (sum / count) - C
        const idx = (y * width + x) * 4
        const value = data[idx] > threshold ? 255 : 0
        resultData[idx] = value
        resultData[idx + 1] = value
        resultData[idx + 2] = value
        resultData[idx + 3] = 255
      }
    }

    return result
  }

  /**
   * 形态学膨胀操作
   * @param {ImageData} imageData - 二值化图像数据
   * @param {number} kernelSize - 结构元素大小
   * @returns {ImageData} 处理后的图像数据
   */
  static dilate(imageData, kernelSize = 3) {
    const width = imageData.width
    const height = imageData.height
    const result = new ImageData(width, height)
    const data = imageData.data
    const resultData = result.data
    const halfKernel = Math.floor(kernelSize / 2)

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        let maxValue = 0

        for (let dy = -halfKernel; dy <= halfKernel; dy++) {
          for (let dx = -halfKernel; dx <= halfKernel; dx++) {
            const nx = x + dx
            const ny = y + dy
            if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
              maxValue = Math.max(maxValue, data[(ny * width + nx) * 4])
            }
          }
        }

        const idx = (y * width + x) * 4
        resultData[idx] = maxValue
        resultData[idx + 1] = maxValue
        resultData[idx + 2] = maxValue
        resultData[idx + 3] = 255
      }
    }

    return result
  }

  /**
   * 形态学腐蚀操作
   * @param {ImageData} imageData - 二值化图像数据
   * @param {number} kernelSize - 结构元素大小
   * @returns {ImageData} 处理后的图像数据
   */
  static erode(imageData, kernelSize = 3) {
    const width = imageData.width
    const height = imageData.height
    const result = new ImageData(width, height)
    const data = imageData.data
    const resultData = result.data
    const halfKernel = Math.floor(kernelSize / 2)

    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        let minValue = 255

        for (let dy = -halfKernel; dy <= halfKernel; dy++) {
          for (let dx = -halfKernel; dx <= halfKernel; dx++) {
            const nx = x + dx
            const ny = y + dy
            if (nx >= 0 && nx < width && ny >= 0 && ny < height) {
              minValue = Math.min(minValue, data[(ny * width + nx) * 4])
            }
          }
        }

        const idx = (y * width + x) * 4
        resultData[idx] = minValue
        resultData[idx + 1] = minValue
        resultData[idx + 2] = minValue
        resultData[idx + 3] = 255
      }
    }

    return result
  }

  static calculateOptimalThreshold(imageData) {
    const data = imageData.data
    const histogram = new Array(256).fill(0)
    let pixelCount = 0

    // 计算灰度直方图
    for (let i = 0; i < data.length; i += 4) {
      histogram[data[i]]++
      pixelCount++
    }

    let sumTotal = 0
    for (let i = 0; i < 256; i++) {
      sumTotal += i * histogram[i]
    }

    let sumBackground = 0
    let weightBackground = 0
    let weightForeground = 0
    let maxVariance = 0
    let optimalThreshold = 0

    // OTSU算法计算最佳阈值
    for (let threshold = 0; threshold < 256; threshold++) {
      weightBackground += histogram[threshold]
      if (weightBackground === 0) continue

      weightForeground = pixelCount - weightBackground
      if (weightForeground === 0) break

      sumBackground += threshold * histogram[threshold]
      const meanBackground = sumBackground / weightBackground
      const meanForeground = (sumTotal - sumBackground) / weightForeground

      const variance = weightBackground * weightForeground * 
                      Math.pow(meanBackground - meanForeground, 2)

      if (variance > maxVariance) {
        maxVariance = variance
        optimalThreshold = threshold
      }
    }

    return optimalThreshold
  }

  /**
   * 字符分割
   * @param {ImageData} imageData - 二值化后的图像数据
   * @returns {Array<{x: number, y: number, width: number, height: number}>} 字符区域数组
   */
  static segmentCharacters(imageData) {
    const width = imageData.width
    const height = imageData.height
    const data = imageData.data
    const visited = new Set()
    const characters = []

    // 深度优先搜索找连通区域
    function dfs(x, y, bounds) {
      const key = y * width + x
      if (visited.has(key)) return
      
      const idx = key * 4
      if (data[idx] === 0) return // 跳过背景像素

      visited.add(key)
      bounds.minX = Math.min(bounds.minX, x)
      bounds.maxX = Math.max(bounds.maxX, x)
      bounds.minY = Math.min(bounds.minY, y)
      bounds.maxY = Math.max(bounds.maxY, y)

      // 遍历8个方向
      const directions = [
        [-1, -1], [-1, 0], [-1, 1],
        [0, -1],          [0, 1],
        [1, -1],  [1, 0],  [1, 1]
      ]

      for (const [dx, dy] of directions) {
        const newX = x + dx
        const newY = y + dy
        if (newX >= 0 && newX < width && newY >= 0 && newY < height) {
          dfs(newX, newY, bounds)
        }
      }
    }

    // 扫描图像寻找字符
    for (let y = 0; y < height; y++) {
      for (let x = 0; x < width; x++) {
        const idx = (y * width + x) * 4
        if (data[idx] === 255 && !visited.has(y * width + x)) {
          const bounds = {
            minX: x, maxX: x,
            minY: y, maxY: y
          }
          dfs(x, y, bounds)

          // 计算字符区域
          const charWidth = bounds.maxX - bounds.minX + 1
          const charHeight = bounds.maxY - bounds.minY + 1
          
          // 过滤掉太小的区域（可能是噪点）
          if (charWidth > 5 && charHeight > 5) {
            characters.push({
              x: bounds.minX,
              y: bounds.minY,
              width: charWidth,
              height: charHeight
            })
          }
        }
      }
    }

    // 按照从左到右的顺序排序字符
    return characters.sort((a, b) => a.x - b.x)
  }
}