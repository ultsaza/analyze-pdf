import { Inter } from "next/font/google"
import DocumentAnalyzer from "@/components/document-analyzer"

const inter = Inter({ subsets: ["latin"] })

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <DocumentAnalyzer />
      </div>
    </main>
  )
}

