import Link from "next/link";
import { Brain, MessageSquare, BarChart3, Database } from "lucide-react";
import FeatureCard from "@/components/FeatureCard";

export default function Home() {
  return (
    <div className="flex-1 flex flex-col items-center px-4 py-8 md:py-16">
      <main className="max-w-5xl w-full flex flex-col items-center mt-8 md:mt-16">
        <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-sm font-medium text-blue-400 mb-8">
          <Brain className="h-4 w-4" />
          LLM学習可視化プラットフォーム
        </div>

        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight text-center mb-6 leading-tight">
          チャットで学ぶ、<br className="md:hidden" />
          <span className="bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">旅行データの世界</span>
        </h1>

        <p className="text-lg text-slate-400 max-w-2xl text-center mb-12 leading-relaxed">
          会話を通じて旅行データを収集し、LLMの学習過程をリアルタイムで可視化。<br />
          RAG（検索拡張生成）の動作を体験しながら、AIの仕組みを理解できます。
        </p>

        <div className="flex flex-col sm:flex-row gap-4 mb-24 w-full justify-center max-w-lg">
          <Link href="/chat" className="flex-1 flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-500 text-white font-semibold py-3.5 px-6 rounded-xl transition-all shadow-[0_0_20px_rgba(37,99,235,0.3)] hover:shadow-[0_0_30px_rgba(37,99,235,0.5)]">
            <MessageSquare className="h-5 w-5" />
            チャットを始める
          </Link>
          <button className="flex-1 flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 text-white border border-white/10 font-semibold py-3.5 px-6 rounded-xl transition-colors">
            <BarChart3 className="h-5 w-5" />
            学習を見る
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 w-full mb-24">
          <FeatureCard
            icon={<MessageSquare className="h-6 w-6" />}
            title="チャット収集"
            description="自然な会話から旅行データを自動抽出・構造化"
          />
          <FeatureCard
            icon={<Brain className="h-6 w-6" />}
            title="学習可視化"
            description="ベクトル化プロセスをリアルタイムで確認"
          />
          <FeatureCard
            icon={<BarChart3 className="h-6 w-6" />}
            title="RAG実装"
            description="検索拡張生成の動作を視覚的に理解"
          />
          <FeatureCard
            icon={<Database className="h-6 w-6" />}
            title="データ管理"
            description="学習データの保存・検索・管理を一元化"
          />
        </div>

        <div className="w-full max-w-4xl border border-white/10 rounded-2xl bg-white/[0.02] p-8 md:p-12 mb-12">
          <h2 className="text-2xl font-bold text-center mb-10 text-white tracking-wide">技術スタック</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10 md:gap-16">
            <div>
              <h3 className="text-blue-400 font-semibold text-lg mb-5 flex items-center gap-2">
                バックエンド
              </h3>
              <ul className="space-y-4 text-slate-300 text-sm md:text-base">
                <li className="flex items-center gap-3"><span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span> FastAPI - 高性能Webフレームワーク</li>
                <li className="flex items-center gap-3"><span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span> OpenAI API - GPT-4/3.5-turbo</li>
                <li className="flex items-center gap-3"><span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span> LangChain - RAG実装</li>
                <li className="flex items-center gap-3"><span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span> ChromaDB - ベクトルデータベース</li>
              </ul>
            </div>
            <div>
              <h3 className="text-blue-400 font-semibold text-lg mb-5 flex items-center gap-2">
                フロントエンド
              </h3>
              <ul className="space-y-4 text-slate-300 text-sm md:text-base">
                <li className="flex items-center gap-3"><span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span> Next.js 16 - React フレームワーク</li>
                <li className="flex items-center gap-3"><span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span> TypeScript - 型安全な開発</li>
                <li className="flex items-center gap-3"><span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span> Tailwind CSS - ユーティリティファースト</li>
                <li className="flex items-center gap-3"><span className="w-1.5 h-1.5 rounded-full bg-slate-500"></span> Recharts - データ可視化</li>
              </ul>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}
