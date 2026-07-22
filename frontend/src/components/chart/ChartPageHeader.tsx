import Logo from "@/components/layout/Logo";
import Button from "@/components/ui/Button";

interface ChartPageHeaderProps {
  title?: string;
}

export default function ChartPageHeader({ title = "紫微斗数命盘" }: ChartPageHeaderProps) {
  return (
    <header className="border-b border-white/5 bg-void/60 backdrop-blur-xl">
      <div className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4 sm:h-16 sm:px-6">
        <Logo size="sm" showSubtitle={false} />

        <h1 className="hidden font-display text-sm font-medium text-white/60 sm:block">
          {title}
        </h1>

        <div className="flex items-center gap-2">
          <Button href="/" variant="ghost" size="sm">
            返回首页
          </Button>
        </div>
      </div>
    </header>
  );
}
