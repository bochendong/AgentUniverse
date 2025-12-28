import { useState, useCallback } from 'react'
import { imageToBase64 } from '../utils/imageUtils'

/**
 * Custom hook for handling image uploads
 */
export function useImageUpload() {
  const [uploadedImages, setUploadedImages] = useState([]) // Array of { file: File, preview: string, base64: string }

  const handleImageChange = useCallback(async (event) => {
    const files = Array.from(event.target.files || [])
    if (files.length === 0) return

    const newImages = []
    for (const file of files) {
      if (file.type.startsWith('image/')) {
        const preview = URL.createObjectURL(file)
        const base64 = await imageToBase64(file)
        newImages.push({ file, preview, base64 })
      }
    }

    setUploadedImages(prev => [...prev, ...newImages])
    // Reset input
    if (event.target) {
      event.target.value = ''
    }
  }, [])

  const removeImage = useCallback((index) => {
    setUploadedImages(prev => {
      const newImages = [...prev]
      URL.revokeObjectURL(newImages[index].preview)
      newImages.splice(index, 1)
      return newImages
    })
  }, [])

  const clearImages = useCallback(() => {
    uploadedImages.forEach(img => URL.revokeObjectURL(img.preview))
    setUploadedImages([])
  }, [uploadedImages])

  // Prepare images for API (base64 format)
  const prepareImagesForAPI = useCallback(() => {
    return uploadedImages
      .filter(img => img.base64)
      .map(img => {
        const mimeType = img.file.type || 'image/jpeg'
        return {
          type: "input_image",
          detail: "auto",
          image_url: img.base64, // base64 already includes data:image/...;base64, prefix
        }
      })
  }, [uploadedImages])

  return {
    uploadedImages,
    handleImageChange,
    removeImage,
    clearImages,
    prepareImagesForAPI,
  }
}

