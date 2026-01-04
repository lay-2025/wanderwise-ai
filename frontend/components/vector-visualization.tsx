"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export function VectorVisualization() {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle>ベクトル空間の可視化</CardTitle>
          <CardDescription>学習データのベクトル分布をリアルタイムで表示</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="2d" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="2d">2D表示</TabsTrigger>
              <TabsTrigger value="3d">3D表示</TabsTrigger>
            </TabsList>
            <TabsContent value="2d" className="mt-4">
              <div className="flex h-[400px] items-center justify-center rounded-lg border border-border bg-muted/30">
                <div className="relative h-full w-full">
                  {/* Simulated scatter plot */}
                  <svg className="h-full w-full" viewBox="0 0 400 400">
                    {/* Grid */}
                    <line x1="0" y1="200" x2="400" y2="200" stroke="currentColor" strokeOpacity="0.1" />
                    <line x1="200" y1="0" x2="200" y2="400" stroke="currentColor" strokeOpacity="0.1" />
                    {/* Data points - cluster 1 (primary) */}
                    <circle cx="150" cy="120" r="4" fill="hsl(var(--chart-1))" />
                    <circle cx="160" cy="130" r="4" fill="hsl(var(--chart-1))" />
                    <circle cx="140" cy="140" r="4" fill="hsl(var(--chart-1))" />
                    <circle cx="170" cy="110" r="4" fill="hsl(var(--chart-1))" />
                    <circle cx="155" cy="125" r="4" fill="hsl(var(--chart-1))" />
                    {/* Data points - cluster 2 (accent) */}
                    <circle cx="280" cy="250" r="4" fill="hsl(var(--chart-2))" />
                    <circle cx="270" cy="260" r="4" fill="hsl(var(--chart-2))" />
                    <circle cx="290" cy="240" r="4" fill="hsl(var(--chart-2))" />
                    <circle cx="285" cy="255" r="4" fill="hsl(var(--chart-2))" />
                    <circle cx="275" cy="245" r="4" fill="hsl(var(--chart-2))" />
                    {/* Data points - cluster 3 */}
                    <circle cx="100" cy="300" r="4" fill="hsl(var(--chart-3))" />
                    <circle cx="110" cy="310" r="4" fill="hsl(var(--chart-3))" />
                    <circle cx="90" cy="290" r="4" fill="hsl(var(--chart-3))" />
                    <circle cx="105" cy="305" r="4" fill="hsl(var(--chart-3))" />
                  </svg>
                </div>
              </div>
            </TabsContent>
            <TabsContent value="3d" className="mt-4">
              <div className="flex h-[400px] items-center justify-center rounded-lg border border-border bg-muted/30">
                <p className="text-sm text-muted-foreground">3D可視化は開発中です</p>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">クラスター1</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <div className="text-2xl font-bold">342</div>
              <div className="text-xs text-muted-foreground">ベクトル</div>
            </div>
            <div className="mt-2 flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-chart-1" />
              <span className="text-xs text-muted-foreground">観光スポット</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">クラスター2</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <div className="text-2xl font-bold">289</div>
              <div className="text-xs text-muted-foreground">ベクトル</div>
            </div>
            <div className="mt-2 flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-chart-2" />
              <span className="text-xs text-muted-foreground">グルメ情報</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium">クラスター3</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline gap-2">
              <div className="text-2xl font-bold">187</div>
              <div className="text-xs text-muted-foreground">ベクトル</div>
            </div>
            <div className="mt-2 flex items-center gap-2">
              <div className="h-3 w-3 rounded-full bg-chart-3" />
              <span className="text-xs text-muted-foreground">宿泊施設</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
