"use client";

import { useState, useRef, useEffect } from "react";
import { Brain, Send } from "lucide-react";

interface Message {
    role: "assistant" | "user";
    content: string;
    time: string;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([
        {
            role: "assistant",
            content: "こんにちは！旅行についてお話ししましょう。最近行った場所や、行きたい場所について教えてください。",
            time: new Date().toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" }),
        }
    ]);
    const [input, setInput] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMessage: Message = {
            role: "user",
            content: input,
            time: new Date().toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" }),
        };

        setMessages((prev) => [...prev, userMessage]);
        setInput("");
        setIsLoading(true);

        try {
            const res = await fetch(`${API_BASE_URL}/api/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ message: userMessage.content }),
            });
            if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
            const data = await res.json();
            setMessages((prev) => [...prev, {
                role: "assistant",
                content: data.response,
                time: new Date().toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" }),
            }]);
        } catch {
            setMessages((prev) => [...prev, {
                role: "assistant",
                content: "申し訳ありません。エラーが発生しました。しばらくしてからもう一度お試しください。",
                time: new Date().toLocaleTimeString("ja-JP", { hour: "2-digit", minute: "2-digit" }),
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-[calc(100vh-4rem)] max-w-5xl mx-auto w-full">
            {/* メッセージエリア */}
            <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-6 mt-4">
                {messages.map((msg, index) => (
                    <div key={index} className={`flex gap-4 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                        {msg.role === 'assistant' && (
                            <div className="flex-shrink-0 mt-1">
                                <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white shadow-[0_0_15px_rgba(37,99,235,0.4)]">
                                    <Brain className="h-6 w-6" />
                                </div>
                            </div>
                        )}
                        <div className={`border rounded-2xl p-4 max-w-[85%] md:max-w-2xl text-slate-200 ${msg.role === 'assistant'
                                ? 'bg-[#121212] border-white/5 rounded-tl-sm'
                                : 'bg-blue-600/10 border-blue-500/20 rounded-tr-sm'
                            }`}>
                            <p className="leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                            <div className="text-xs text-slate-500 mt-3">{msg.time}</div>
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="flex gap-4">
                        <div className="flex-shrink-0 mt-1">
                            <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center text-white">
                                <Brain className="h-6 w-6" />
                            </div>
                        </div>
                        <div className="border rounded-2xl p-4 bg-[#121212] border-white/5 rounded-tl-sm">
                            <div className="flex gap-1">
                                <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.3s]" />
                                <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500 [animation-delay:-0.15s]" />
                                <div className="h-2 w-2 animate-bounce rounded-full bg-blue-500" />
                            </div>
                        </div>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            {/* 入力エリア */}
            <div className="p-4 md:p-6 pb-8 mt-auto">
                <div className="max-w-4xl mx-auto relative">
                    <div className="relative flex items-end gap-2 bg-[#121212] border border-white/10 rounded-2xl p-2 focus-within:border-blue-500/50 shadow-lg transition-colors">
                        <textarea
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === "Enter" && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSend();
                                }
                            }}
                            placeholder="旅行について話してください..."
                            className="flex-1 bg-transparent text-white placeholder-slate-500 resize-none outline-none max-h-32 min-h-[44px] py-3 px-4 text-base"
                            rows={1}
                            disabled={isLoading}
                        />
                        <button
                            onClick={handleSend}
                            className="p-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl transition-all shadow-md hover:shadow-[0_0_15px_rgba(37,99,235,0.5)] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-none mb-1 mr-1"
                            disabled={!input.trim() || isLoading}
                        >
                            <Send className="h-5 w-5" />
                        </button>
                    </div>
                    <div className="text-center text-xs text-slate-500 mt-4 font-medium tracking-wide">
                        あなたの会話から旅行データを学習し、より良い回答を提供します
                    </div>
                </div>
            </div>
        </div>
    );
}
