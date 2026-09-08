import React from 'react';

export type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'outline' | 'ghost';
export type ButtonSize = 'sm' | 'md' | 'lg';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  children: React.ReactNode;
}

export function Button({
  variant = 'secondary',
  size = 'md',
  className = '',
  disabled,
  children,
  ...props
}: ButtonProps) {
  const getStyles = () => {
    let base = 'inline-flex items-center justify-center font-medium transition-colors cursor-pointer disabled:cursor-not-allowed disabled:opacity-50 ';
    
    // sizes
    if (size === 'sm') base += 'px-2.5 py-1 text-xs rounded ';
    else if (size === 'lg') base += 'px-5 py-2.5 text-base rounded-md ';
    else base += 'px-3.5 py-1.5 text-sm rounded-md ';

    // variant styles using inline CSS variables / utility classes
    return base + className;
  };

  const getInlineStyle = (): React.CSSProperties => {
    switch (variant) {
      case 'primary':
        return {
          backgroundColor: 'var(--text-accent)',
          color: 'var(--surface-base)',
          border: '1px solid transparent',
          fontWeight: 600,
        };
      case 'danger':
        return {
          backgroundColor: 'var(--status-critical-bg)',
          color: 'var(--status-critical)',
          border: '1px solid var(--status-critical)',
        };
      case 'outline':
        return {
          backgroundColor: 'transparent',
          color: 'var(--text-primary)',
          border: '1px solid var(--surface-border-strong)',
        };
      case 'ghost':
        return {
          backgroundColor: 'transparent',
          color: 'var(--text-secondary)',
          border: '1px solid transparent',
        };
      case 'secondary':
      default:
        return {
          backgroundColor: 'var(--surface-elevated)',
          color: 'var(--text-primary)',
          border: '1px solid var(--surface-border)',
        };
    }
  };

  return (
    <button
      className={getStyles()}
      style={getInlineStyle()}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}
