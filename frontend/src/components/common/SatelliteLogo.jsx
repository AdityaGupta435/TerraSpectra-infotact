import React from "react";

export default function SatelliteLogo({ size = 38 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="22" cy="28" r="15" fill="#e0f2fe" stroke="#0284c7" strokeWidth="2" />
      <path d="M10 31C15 26 24 25 34 31" stroke="#16a34a" strokeWidth="2.8" strokeLinecap="round" />
      <path d="M12 36C18 32 25 32 32 36" stroke="#15803d" strokeWidth="2.8" strokeLinecap="round" />
      <path d="M16 25C16 20 20 18 22 22C24 18 28 20 28 25" fill="#22c55e" />
      <g transform="translate(27, 4) rotate(32)">
        <rect x="4" y="3" width="6" height="8" rx="1.5" fill="#0369a1" />
        <rect x="0" y="5" width="4" height="4" fill="#38bdf8" />
        <rect x="10" y="5" width="4" height="4" fill="#38bdf8" />
        <path d="M5 12C6 14 8 14 9 12" stroke="#0284c7" strokeWidth="1.5" strokeLinecap="round" />
      </g>
    </svg>
  );
}
