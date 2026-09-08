'use client';

import React from 'react';
import { usePathname } from 'next/navigation';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { GlobalContextBar } from './GlobalContextBar';
import { ScenarioBanner } from '../state/ScenarioBanner';
import { GlobalSearchModal } from './GlobalSearchModal';
import { OperationalProvider } from '../../context/OperationalContext';
import { WORKSPACE_CONFIG } from '../../config/workspaceConfig';
import { SearchProvider } from '../../hooks/useGlobalSearch';

interface AppShellProps {
  title?: string;
  eyebrow?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
}

export function AppShell({ title, eyebrow, actions, children }: AppShellProps) {
  const pathname = usePathname();
  const config = WORKSPACE_CONFIG[pathname] || { title: 'Workspace', eyebrow: 'Operational View' };

  const finalTitle = title || config.title;
  const finalEyebrow = eyebrow || config.eyebrow;

  return (
    <OperationalProvider>
      <SearchProvider>
        <div className="app-shell-root">
          <Sidebar />
          <main className="app-main">
            <TopBar title={finalTitle} eyebrow={finalEyebrow} actions={actions} />
            <GlobalContextBar />
            <ScenarioBanner />
            <div className="workspace-container">{children}</div>
          </main>
          <GlobalSearchModal />
        </div>
      </SearchProvider>
    </OperationalProvider>
  );
}
