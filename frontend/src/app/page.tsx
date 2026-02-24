import Link from "next/link";
import { Brain, MessageSquare, BarChart3, Database } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-white text-slate-900 flex flex-col items-center justify-center p-8">
      <main className="max-w-3xl w-full flex flex-col items-center text-center space-y-8">

        <div className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-4 py-1.5 text-sm font-medium text-blue-700">
          <Brain className="h-4 w-4" />
          LLM学習可視化プラットフォーム
        </div>

        <h1 className="text-4xl md:text-5xl font-extrabold tracking-tight">
          チャットで学ぶ、<br className="md:hidden" />
          <span className="text-blue-600">旅行データの世界</span>
        </h1>

        <p className="text-lg text-slate-600 max-w-2xl">
          これは新しく再構築されたローカル開発用フロントエンドです。<br />
          Next.js (App Router) と Tailwind CSS により、エラーなく高速に動作します。
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-lg mt-8">
          <button className="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors">
            <MessageSquare className="h-5 w-5" />
            チャットを始める
          </button>
          <button className="flex items-center justify-center gap-2 bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 font-semibold py-3 px-6 rounded-lg transition-colors">
            <BarChart3 className="h-5 w-5" />
            学習を見る
          </button>
        </div>

      </main>

      <footer className="mt-20 text-sm text-slate-500">
        WanderWise AI - Local Development Environment
      </footer>
    </div>
  );
}
