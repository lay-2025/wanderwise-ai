"use client"

import { useState } from "react"
import Link from "next/link"
import { Brain, Search, TrendingUp, Database, FileText, Activity } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { DataCollectionPanel } from "@/components/data-collection-panel"
import { VectorVisualization } from "@/components/vector-visualization"

export function LearningDashboard() {
  const [searchQuery, setSearchQuery] = useState("")

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-2">
            <Brain className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-semibold">学習管理ダッシュボード</h1>
          </Link>
          <Link href="/chat">
            <Button variant="outline">チャットに戻る</Button>
          </Link>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8">
        {/* Stats Overview */}
        <div className="mb-8 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">総ドキュメント数</CardTitle>
              <FileText className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">1,247</div>
              <p className="text-xs text-muted-foreground">+12% from last week</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">ベクトル数</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">8,392</div>
              <p className="text-xs text-muted-foreground">+23% from last week</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">学習進捗</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">87%</div>
              <p className="text-xs text-muted-foreground">Processing phase 3/4</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium">システム状態</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-primary">Active</div>
              <p className="text-xs text-muted-foreground">All systems operational</p>
            </CardContent>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs defaultValue="visualization" className="space-y-4">
          <TabsList>
            <TabsTrigger value="visualization">ベクトル可視化</TabsTrigger>
            <TabsTrigger value="collection">データ収集</TabsTrigger>
            <TabsTrigger value="search">検索</TabsTrigger>
          </TabsList>

          <TabsContent value="visualization" className="space-y-4">
            <VectorVisualization />
          </TabsContent>

          <TabsContent value="collection" className="space-y-4">
            <DataCollectionPanel />
          </TabsContent>

          <TabsContent value="search" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>学習データ検索</CardTitle>
                <CardDescription>ベクトルデータベースから類似ドキュメントを検索</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex gap-2">
                  <Input
                    placeholder="検索クエリを入力..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  <Button>
                    <Search className="h-4 w-4" />
                  </Button>
                </div>
                <div className="mt-6 space-y-4">
                  <div className="rounded-lg border border-border bg-card p-4">
                    <div className="mb-2 flex items-center justify-between">
                      <span className="text-sm font-medium">京都の観光スポット</span>
                      <span className="text-xs text-muted-foreground">類似度: 0.94</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      京都には清水寺、金閣寺、伏見稲荷大社など多くの歴史的な観光スポットがあります...
                    </p>
                  </div>
                  <div className="rounded-lg border border-border bg-card p-4">
                    <div className="mb-2 flex items-center justify-between">
                      <span className="text-sm font-medium">日本の旅館体験</span>
                      <span className="text-xs text-muted-foreground">類似度: 0.87</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      伝統的な日本旅館では、温泉、懐石料理、おもてなしの文化を体験できます...
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}
