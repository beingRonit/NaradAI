"use client";

import { useEffect, useRef } from "react";
import createGlobe from "cobe";

interface CobeGlobeProps {
  className?: string;
}

export function CobeGlobe({ className }: CobeGlobeProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const phiRef = useRef(0);

  useEffect(() => {
    if (!canvasRef.current) return;

    const globe = createGlobe(canvasRef.current, {
      devicePixelRatio: 2,
      width: 1000,
      height: 1000,
      phi: 0,
      theta: 0.3,
      dark: 1,
      diffuse: 1.5,
      mapSamples: 16000,
      mapBrightness: 8,
      baseColor: [0.35, 0.2, 0.6],
      markerColor: [1, 1, 1],
      glowColor: [0.55, 0.35, 0.95],
      markers: [
        { location: [37.7749, -122.4194], size: 0.06 },
        { location: [40.7128, -74.006], size: 0.06 },
        { location: [51.5074, -0.1278], size: 0.05 },
        { location: [48.8566, 2.3522], size: 0.05 },
        { location: [35.6762, 139.6503], size: 0.06 },
        { location: [-33.8688, 151.2093], size: 0.04 },
        { location: [55.7558, 37.6173], size: 0.05 },
        { location: [1.3521, 103.8198], size: 0.04 },
        { location: [19.4326, -99.1332], size: 0.04 },
        { location: [-22.9068, -43.1729], size: 0.05 },
      ],
    });

    let frameId: number;
    const animate = () => {
      phiRef.current += 0.005;
      globe.update({ phi: phiRef.current });
      frameId = requestAnimationFrame(animate);
    };
    frameId = requestAnimationFrame(animate);

    return () => {
      globe.destroy();
      cancelAnimationFrame(frameId);
    };
  }, []);

  return (
    <div className={className} style={{ filter: "drop-shadow(0 0 30px rgba(139, 92, 246, 0.4))" }}>
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{
          contain: "layout paint size",
          opacity: 1,
          transition: "opacity 1s ease",
        }}
      />
    </div>
  );
}
