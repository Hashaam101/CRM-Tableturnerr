import React from 'react';

interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Skeleton({ className, ...props }: SkeletonProps) {
  return (
    <div 
      className={`animate-shimmer rounded-md ${className || ''}`} 
      {...props} 
    />
  );
}
