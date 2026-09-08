'use client';

import React from 'react';
import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { GlobalContextBar } from './GlobalContextBar';
import { ScenarioBanner } from '../state/ScenarioBanner';
import { GlobalSearchModal } from './GlobalSearchModal';
import { OperationalProvider } from '../../context/OperationalContext';

interface AppShellProps {
  title: string;
  eyebrow?: string;
  actions?: React.ReactNode;
  children: React.ReactNode;
}

export function AppShell({ title, eyebrow, actions, children }: AppShellProps) {
  return (
    <OperationalProvider>
      <div className="app-shell-root">
        <Sidebar />
        <main className="app-main">
          <TopBar title={title} eyebrow={eyebrow} actions={actions} />
          <GlobalContextBar />
          <ScenarioBanner />
          <div className="workspace-container">{children}</div>
        </main>
        <GlobalSearchModal />
      </div>
    </OperationalProvider>
  );
}
