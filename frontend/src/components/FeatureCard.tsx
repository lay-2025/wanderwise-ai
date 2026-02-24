import { ReactNode } from "react";

export interface FeatureCardProps {
    icon: ReactNode;
    title: string;
    description: string;
}

export default function FeatureCard({ icon, title, description }: FeatureCardProps) {
    return (
        <div className="group rounded-xl border border-white/10 bg-white/5 p-6 hover:bg-white/10 transition-all hover:border-blue-500/50 hover:shadow-[0_0_15px_rgba(59,130,246,0.15)] flex flex-col h-full">
            <div className="mb-4 inline-flex h-12 w-12 items-center justify-center rounded-lg bg-white/5 text-blue-400 group-hover:bg-blue-500/20 group-hover:text-blue-300 transition-colors">
                {icon}
            </div>
            <h3 className="mb-3 font-bold text-white text-lg">{title}</h3>
            <p className="text-sm text-slate-400 leading-relaxed text-left">{description}</p>
        </div>
    );
}
