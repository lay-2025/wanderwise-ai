"use client"

import { useState } from "react"
import { Upload, File, CheckCircle2, Clock, XCircle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"

interface Document {
  id: string
  name: string
  status: "pending" | "processing" | "completed" | "error"
  progress: number
  vectors: number
}

export function DataCollectionPanel() {
  const [documents] = useState<Document[]>([
    {
      id: "1",
      name: "東京観光ガイド.pdf",
      status: "completed",
      progress: 100,
      vectors: 342,
    },
    {
      id: "2",
      name: "京都の歴史.txt",
      status: "processing",
      progress: 67,
      vectors: 189,
    },
    {
      id: "3",
      name: "北海道グルメ情報.md",
      status: "pending",
      progress: 0,
      vectors: 0,
    },
  ])

  const getStatusIcon = (status: Document["status"]) => {
    switch (status) {
      case "completed":
        return <CheckCircle2 className="h-5 w-5 text-primary" />
      case "processing":
        return <Clock className="h-5 w-5 text-accent animate-pulse" />
      case "error":
        return <XCircle className="h-5 w-5 text-destructive" />
      default:
        return <File className="h-5 w-5 text-muted-foreground" />
    }
  }

  const getStatusText = (status: Document["status"]) => {
    switch (status) {
      case "completed":
        return "完了"
      case "processing":
        return "処理中"
      case "error":
        return "エラー"
      default:
        return "待機中"
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>ドキュメントアップロード</CardTitle>
          <CardDescription>学習用の旅行データをアップロードしてベクトル化</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-border bg-muted/50 p-12 text-center">
            <Upload className="mb-4 h-12 w-12 text-muted-foreground" />
            <p className="mb-2 text-sm font-medium">ファイルをドラッグ&ドロップ</p>
            <p className="mb-4 text-xs text-muted-foreground">または クリックしてファイルを選択</p>
            <Button>ファイルを選択</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>処理状況</CardTitle>
          <CardDescription>アップロードされたドキュメントの処理状況</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {documents.map((doc) => (
              <div key={doc.id} className="rounded-lg border border-border bg-card p-4">
                <div className="mb-3 flex items-start justify-between">
                  <div className="flex items-start gap-3">
                    {getStatusIcon(doc.status)}
                    <div>
                      <p className="text-sm font-medium">{doc.name}</p>
                      <p className="text-xs text-muted-foreground">
                        {getStatusText(doc.status)}
                        {doc.vectors > 0 && ` • ${doc.vectors} ベクトル`}
                      </p>
                    </div>
                  </div>
                  <span className="text-xs text-muted-foreground">{doc.progress}%</span>
                </div>
                {doc.status === "processing" && <Progress value={doc.progress} className="h-2" />}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
