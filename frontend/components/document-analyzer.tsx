"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Loader2, FileText, X, Copy } from "lucide-react"
import { toast } from "@/components/ui/use-toast"
import PDFViewer from "@/components/pdf-viewer"

export default function DocumentAnalyzer() {
  const [files, setFiles] = useState<File[]>([])
  const [analyzing, setAnalyzing] = useState(false)
  const [result, setResult] = useState<string | null>(null)
  const [selectedFile, setSelectedFile] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      // PDFファイルのみ許可
      const pdfFiles = Array.from(e.target.files).filter((file) => file.type === "application/pdf")
      setFiles(pdfFiles)
      if (pdfFiles.length > 0) {
        const url = URL.createObjectURL(pdfFiles[0])
        setSelectedFile(url)
      }
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const pdfFiles = Array.from(e.dataTransfer.files).filter((file) => file.type === "application/pdf")
      setFiles(pdfFiles)
      if (pdfFiles.length > 0) {
        const url = URL.createObjectURL(pdfFiles[0])
        setSelectedFile(url)
      }
    }
  }

  const removeFile = (index: number) => {
    const newFiles = [...files]
    newFiles.splice(index, 1)
    setFiles(newFiles)
    if (newFiles.length > 0) {
      const url = URL.createObjectURL(newFiles[0])
      setSelectedFile(url)
    } else {
      setSelectedFile(null)
    }
  }

  const getTotalSize = () => {
    return files.reduce((acc, file) => acc + file.size, 0)
  }

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 KB"
    const k = 1024
    const sizes = ["バイト", "KB", "MB", "GB"]
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Number.parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i]
  }

  const analyzeDocuments = async () => {
    if (files.length === 0) {
      toast({
        title: "エラー",
        description: "ファイルが選択されていません。",
        variant: "destructive",
      })
      return
    }

    setAnalyzing(true)
    setResult(null)

    try {
      const formData = new FormData()
      files.forEach((file) => {
        formData.append("files", file)
      })

      const response = await fetch("http://localhost:8000/api/analyze", {
        method: "POST",
        body: formData,
      })

      if (!response.ok) {
        throw new Error(`エラー: ${response.status}`)
      }

      const data = await response.json()
      setResult(data.result)
    } catch (error) {
      console.error("分析中にエラーが発生しました:", error)
      toast({
        title: "エラー",
        description: "文書の分析中にエラーが発生しました。",
        variant: "destructive",
      })
    } finally {
      setAnalyzing(false)
    }
  }

  const copyToClipboard = () => {
    if (result) {
      navigator.clipboard.writeText(result)
      toast({
        title: "コピーしました",
        description: "結果をクリップボードにコピーしました。",
      })
    }
  }

  return (
    <div className="bg-white shadow rounded-lg">
      <div className="text-2xl font-bold p-6 border-b">文書解析アプリケーション</div>
      <div className="flex flex-col md:flex-row">
        <div className="md:w-1/2 p-6 border-r">
          <div className="mb-6">
            <div className="flex items-center mb-2">
              <FileText className="mr-2 h-5 w-5 text-gray-500" />
              <h2 className="text-lg font-medium">選択されたPDFファイル</h2>
            </div>
            <div
              className="border border-dashed border-gray-300 rounded-lg p-4 bg-gray-50 text-center cursor-pointer hover:bg-gray-100 transition"
              onClick={() => fileInputRef.current?.click()}
              onDragOver={handleDragOver}
              onDrop={handleDrop}
            >
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                className="hidden"
                accept="application/pdf"
                multiple
              />
              {files.length === 0 ? (
                <div className="py-8">
                  <p className="text-gray-500 mb-2">
                    PDFファイルをドラッグ＆ドロップするか、クリックして選択してください
                  </p>
                  <Button variant="outline" size="sm">
                    ファイルを選択
                  </Button>
                </div>
              ) : (
                <div className="space-y-2">
                  {files.map((file, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between bg-white p-2 rounded border text-left"
                    >
                      <div className="flex items-center overflow-hidden">
                        <FileText className="flex-shrink-0 h-5 w-5 text-blue-500 mr-2" />
                        <span className="truncate">{file.name}</span>
                        <span className="ml-2 text-xs text-gray-500">({formatBytes(file.size)})</span>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation()
                          removeFile(index)
                        }}
                        className="text-gray-500 hover:text-red-500"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
            {files.length > 0 && (
              <div className="mt-2 text-sm text-gray-500 text-right">
                {files.length} ファイル ({formatBytes(getTotalSize())})
              </div>
            )}
          </div>

          <Button className="w-full mb-6" disabled={files.length === 0 || analyzing} onClick={analyzeDocuments}>
            {analyzing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                解析中...
              </>
            ) : (
              "文書を解析"
            )}
          </Button>

          {result && (
            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-lg font-medium">解析結果:</h2>
                <Button variant="outline" size="sm" onClick={copyToClipboard} className="ml-2">
                  <Copy className="h-4 w-4 mr-1" />
                  コピー
                </Button>
              </div>
              <div className="bg-gray-50 p-4 rounded-lg border relative">
                <pre className="text-sm overflow-auto max-h-[500px]">{result}</pre>
              </div>
            </div>
          )}
        </div>

        <div className="md:w-1/2 p-6">
          <h2 className="text-lg font-medium mb-4">PDFプレビュー</h2>
          {selectedFile ? (
            <PDFViewer fileUrl={selectedFile} />
          ) : (
            <div className="border rounded-lg p-8 bg-gray-50 text-center text-gray-500 h-[600px] flex items-center justify-center">
              <p>PDFファイルを選択するとここにプレビューが表示されます</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

