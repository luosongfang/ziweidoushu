export default function PrivacyNotice({ className = "" }: { className?: string }) {
  return (
    <p className={`text-xs leading-relaxed text-paper/35 ${className}`}>
      你的信息仅用于生成个人分析档案，不会用于公开展示。
    </p>
  );
}
