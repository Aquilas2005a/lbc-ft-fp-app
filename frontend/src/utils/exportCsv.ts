export type CsvRow = Record<string, string | number | null | undefined>

function escapeCell(value: CsvRow[string]): string {
  const normalized = value == null ? '' : String(value)
  return /[\n\r",;]/.test(normalized)
    ? `"${normalized.replace(/"/g, '""')}"`
    : normalized
}

export function downloadCsv(filename: string, rows: CsvRow[]) {
  if (rows.length === 0) return false

  const headers = Object.keys(rows[0])
  const csv = [
    headers.map(escapeCell).join(';'),
    ...rows.map((row) => headers.map((header) => escapeCell(row[header])).join(';')),
  ].join('\r\n')

  const blob = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  link.click()
  URL.revokeObjectURL(url)
  return true
}
