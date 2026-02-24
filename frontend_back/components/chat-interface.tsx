"use client"

import { useState } from "react"
import Link from "next/link"
import { Brain, Send, Sparkles, User, Bot } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  timestamp: Date
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "こんにちは！旅行についてお話ししましょう。最近行った場所や、行きたい場所について教えてください。",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    // Simulate API call
    setTimeout(() => {
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: "興味深いですね！そちらの観光スポットや体験について、もう少し詳しく教えていただけますか？",
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
      setIsLoading(false)
    }, 1000)
  }

  return (
    <div className="flex h-screen flex-col">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-2">
            <Brain className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-semibold">Travel Chat Assistant</h1>
          </Link>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 rounded-full border border-primary/20 bg-primary/10 px-3 py-1.5 text-sm text-primary">
              <Sparkles className="h-4 w-4" />
              学習中
            </div>
            <Link href="/learning">
              <Button variant="outline" size="sm">
                学習管理
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Chat Messages */}
      <ScrollArea className="flex-1">
        <div className="container mx-auto max-w-4xl px-4 py-8">
          <div className="space-y-6">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-4 ${message.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {message.role === "assistant" && (
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                    <Bot className="h-5 w-5" />
                  </div>
                )}
                <Card
                  className={`max-w-[80%] ${
                    message.role === "user" ? "bg-primary text-primary-foreground" : "bg-card"
                  }`}
                >
                  <div className="p-4">
                    <p className="text-sm leading-relaxed">{message.content}</p>
                    <p
                      className={`mt-2 text-xs ${
                        message.role === "user" ? "text-primary-foreground/70" : "text-muted-foreground"
                      }`}
                    >
                      {message.timestamp.toLocaleTimeString("ja-JP", {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </p>
                  </div>
                </Card>
                {message.role === "user" && (
                  <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent text-accent-foreground">
                    <User className="h-5 w-5" />
                  </div>
                )}
              </div>
            ))}
            {isLoading && (
              <div className="flex gap-4">
                <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                  <Bot className="h-5 w-5" />
                </div>
                <Card className="bg-card">
                  <div className="p-4">
                    <div className="flex gap-1">
                      <div className="h-2 w-2 animate-bounce rounded-full bg-primary [animation-delay:-0.3s]" />
                      <div className="h-2 w-2 animate-bounce rounded-full bg-primary [animation-delay:-0.15s]" />
                      <div className="h-2 w-2 animate-bounce rounded-full bg-primary" />
                    </div>
                  </div>
                </Card>
              </div>
            )}
          </div>
        </div>
      </ScrollArea>

      {/* Input Area */}
      <div className="border-t border-border bg-card">
        <div className="container mx-auto max-w-4xl px-4 py-4">
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              placeholder="旅行について話してください..."
              className="flex-1"
              disabled={isLoading}
            />
            <Button onClick={handleSend} disabled={isLoading || !input.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            あなたの会話から旅行データを学習し、より良い回答を提供します
          </p>
        </div>
      </div>
    </div>
  )
}
