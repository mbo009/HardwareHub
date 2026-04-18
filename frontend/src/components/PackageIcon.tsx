import React from "react";

type PackageIconProps = {
  size?: number;
  color?: string;
  strokeWidth?: number;
};

export default function PackageIcon({
  size = 22,
  color = "currentColor",
  strokeWidth = 1.8,
}: PackageIconProps) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <path
        d="M12 3L4 7.5V16.5L12 21L20 16.5V7.5L12 3Z"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinejoin="round"
      />
      <path
        d="M12 3V12M12 12L20 7.5M12 12L4 7.5"
        stroke={color}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

