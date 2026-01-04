import Link from "next/link"
import { MessageSquare, Brain, BarChart3, Database } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <div className="flex items-center gap-2">
            <Brain className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-semibold">Travel Chat Assistant</h1>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/chat">
              <Button variant="ghost">チャット</Button>
            </Link>
            <Link href="/learning">
              <Button variant="ghost">学習管理</Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="mx-auto max-w-3xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-4 py-1.5 text-sm text-primary">
            <Brain className="h-4 w-4" />
            LLM学習可視化プラットフォーム
          </div>
          <h2 className="mb-6 text-5xl font-bold leading-tight text-balance">
            チャットで学ぶ、
            <br />
            <span className="text-primary">旅行データの世界</span>
          </h2>
          <p className="mb-8 text-lg text-muted-foreground text-balance">
            会話を通じて旅行データを収集し、LLMの学習過程をリアルタイムで可視化。
            RAG（検索拡張生成）の動作を体験しながら、AIの仕組みを理解できます。
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link href="/chat">
              <Button size="lg" className="gap-2">
                <MessageSquare className="h-5 w-5" />
                チャットを始める
              </Button>
            </Link>
            <Link href="/learning">
              <Button size="lg" variant="outline" className="gap-2 bg-transparent">
                <BarChart3 className="h-5 w-5" />
                学習を見る
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader>
              <MessageSquare className="mb-2 h-8 w-8 text-primary" />
              <CardTitle>チャット収集</CardTitle>
              <CardDescription>自然な会話から旅行データを自動抽出・構造化</CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <Brain className="mb-2 h-8 w-8 text-accent" />
              <CardTitle>学習可視化</CardTitle>
              <CardDescription>ベクトル化プロセスをリアルタイムで確認</CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <BarChart3 className="mb-2 h-8 w-8 text-chart-3" />
              <CardTitle>RAG実装</CardTitle>
              <CardDescription>検索拡張生成の動作を視覚的に理解</CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <Database className="mb-2 h-8 w-8 text-chart-4" />
              <CardTitle>データ管理</CardTitle>
              <CardDescription>学習データの保存・検索・管理を一元化</CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="container mx-auto px-4 py-16">
        <Card className="border-primary/20 bg-card/50">
          <CardHeader>
            <CardTitle className="text-center text-2xl">技術スタック</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid gap-8 md:grid-cols-2">
              <div>
                <h3 className="mb-4 font-semibold text-primary">バックエンド</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>• FastAPI - 高性能Webフレームワーク</li>
                  <li>• OpenAI API - GPT-4/3.5-turbo</li>
                  <li>• LangChain - RAG実装</li>
                  <li>• ChromaDB - ベクトルデータベース</li>
                </ul>
              </div>
              <div>
                <h3 className="mb-4 font-semibold text-accent">フロントエンド</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>• Next.js 16 - React フレームワーク</li>
                  <li>• TypeScript - 型安全な開発</li>
                  <li>• Tailwind CSS - ユーティリティファースト</li>
                  <li>• Recharts - データ可視化</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
      </section>
    </div>
  )
}
