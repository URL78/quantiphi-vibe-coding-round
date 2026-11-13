/**
 * useAutoSync – transparently syncs a GitHub profile if it isn't cached yet.
 *
 * Usage:
 *   const { syncing, syncError, ensureSync } = useAutoSync();
 *   const ok = await ensureSync('torvalds');
 *   if (ok) { ... proceed ... }
 */

import { useState, useCallback } from 'react';
import { syncProfile } from '../services/api';

export function useAutoSync() {
  const [syncing, setSyncing] = useState(false);
  const [syncError, setSyncError] = useState('');

  const ensureSync = useCallback(async (username) => {
    if (!username) return false;
    setSyncing(true);
    setSyncError('');
    try {
      await syncProfile(username.trim(), false);
      return true;
    } catch (err) {
      const detail = err?.response?.data?.detail;
      const msg =
        typeof detail === 'string'
          ? detail
          : detail?.message || 'Failed to load GitHub profile. Check the username.';
      setSyncError(msg);
      return false;
    } finally {
      setSyncing(false);
    }
  }, []);

  return { syncing, syncError, ensureSync };
}
