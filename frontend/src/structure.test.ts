// @vitest-environment node
import { existsSync, statSync } from 'node:fs'
import { join } from 'node:path'
import { describe, test, expect } from 'vitest'

const srcDir = join(process.cwd(), 'src')

const ALL_NINE_DIRS = [
  'assets',
  'components',
  'hooks',
  'layouts',
  'pages',
  'router',
  'services',
  'types',
  'utils',
]

const DIRS_REQUIRING_GITKEEP = ['assets', 'hooks', 'services', 'types', 'utils']

describe('frontend/src directory structure (issue #9)', () => {
  test('all nine required directories exist under frontend/src/', () => {
    for (const dir of ALL_NINE_DIRS) {
      expect(existsSync(join(srcDir, dir)), `${dir}/ must exist`).toBe(true)
    }
  })

  describe('.gitkeep files exist in previously-empty directories', () => {
    test.each(DIRS_REQUIRING_GITKEEP)('%s/.gitkeep exists', (dir) => {
      const gitkeepPath = join(srcDir, dir, '.gitkeep')
      expect(existsSync(gitkeepPath), `${gitkeepPath} must be present`).toBe(true)
    })
  })

  describe('.gitkeep files are zero-byte', () => {
    test.each(DIRS_REQUIRING_GITKEEP)('%s/.gitkeep is empty (zero bytes)', (dir) => {
      const gitkeepPath = join(srcDir, dir, '.gitkeep')
      expect(existsSync(gitkeepPath), `${gitkeepPath} must exist before size check`).toBe(true)
      expect(statSync(gitkeepPath).size, `${gitkeepPath} must be zero-byte`).toBe(0)
    })
  })
})
