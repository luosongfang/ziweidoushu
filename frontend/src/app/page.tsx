import StarryBackground from "@/components/background/StarryBackground";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import HeroSection from "@/components/home/HeroSection";
import ProductIntro from "@/components/home/ProductIntro";
import AILifePlanning from "@/components/home/AILifePlanning";

export default function HomePage() {
  return (
    <>
      <StarryBackground />
      <Header />
      <main>
        <HeroSection />
        <ProductIntro />
        <AILifePlanning />
      </main>
      <Footer />
    </>
  );
}
