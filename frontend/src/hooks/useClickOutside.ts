'use client'

import { useEffect, useRef, type RefObject } from 'react'

/** Fires `onOutsideClick` when a mousedown lands outside the returned ref's node. */
export function useClickOutside<T extends HTMLElement>(
  onOutsideClick: () => void,
): RefObject<T | null> {
  const ref = useRef<T | null>(null)

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        onOutsideClick()
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [onOutsideClick])

  return ref
}
