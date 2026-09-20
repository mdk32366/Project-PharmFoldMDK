import { describe, it, expect } from 'vitest'
import { MemoryRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { render, screen, waitFor } from '@testing-library/react'

function Where() {
  const loc = useLocation()
  return <div data-testid="where">{loc.pathname}</div>
}

describe('D-169 /coverage redirect', () => {
  it('navigating to /coverage lands on /targets (replace)', async () => {
    render(
      <MemoryRouter initialEntries={['/coverage']}>
        <Routes>
          <Route path="/coverage" element={<Navigate to="/targets" replace />} />
          <Route path="/targets" element={<Where />} />
          <Route path="*" element={<div data-testid="where">story</div>} />
        </Routes>
      </MemoryRouter>,
    )
    await waitFor(() => expect(screen.getByTestId('where').textContent).toBe('/targets'))
  })
})
