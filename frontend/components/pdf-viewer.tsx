"use client"

import { useEffect, useState } from "react"
import { Loader2 } from "lucide-react"

interface PDFViewerProps {
  fileUrl: string
}

const PDFViewer = ({ fileUrl }: PDFViewerProps) => {
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    // PDFファイルがロードされたらローディング状態を解除
    const timer = setTimeout(() => {
      setLoading(false)
    }, 1000)

    return () => clearTimeout(timer)
  }, [fileUrl])

  return (
    <div className="w-full h-[600px] border rounded-lg overflow-hidden bg-gray-50 relative">
      {loading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-50 bg-opacity-80 z-10">
          <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
        </div>
      )}
      <iframe src={fileUrl} className="w-full h-full" title="PDF Viewer" onLoad={() => setLoading(false)} />
    </div>
  )
}

export default PDFViewer

