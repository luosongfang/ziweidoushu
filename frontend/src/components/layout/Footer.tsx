import Logo from "./Logo";
import { SITE } from "@/lib/constants";

export default function Footer() {
  return (
    <footer id="about" className="border-t border-white/5 bg-void-50/50">
      <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center gap-6 text-center md:flex-row md:justify-between md:text-left">
          <Logo size="sm" />
          <p className="max-w-md text-sm text-white/40">
            {SITE.description}
          </p>
        </div>
        <div className="mt-8 border-t border-white/5 pt-8 text-center text-xs text-white/30">
          © {new Date().getFullYear()} {SITE.name}. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
