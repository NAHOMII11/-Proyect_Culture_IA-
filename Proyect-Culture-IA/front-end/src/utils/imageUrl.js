const MOJIBAKE_REPLACEMENTS = [
  [/a\uFFFDrea/gi, 'a%C3%A9rea'],
  [/a�rea/gi, 'a%C3%A9rea'],
  [/Bogot\uFFFD/gi, 'Bogot%C3%A1'],
  [/Bogot�/g, 'Bogot%C3%A1'],
  [/El\uFFFDas/gi, 'El%C3%ADas'],
  [/El�as/gi, 'El%C3%ADas'],
  [/Gait\uFFFDn/gi, 'Gait%C3%A1n'],
  [/Gait�n/gi, 'Gait%C3%A1n'],
  [/Nari\uFFFDo/gi, 'Nari%C3%B1o'],
  [/Nari�o/gi, 'Nari%C3%B1o'],
  [/Bol\uFFFDvar/gi, 'Bol%C3%ADvar'],
  [/Bol�var/gi, 'Bol%C3%ADvar'],
]

function encodePathSegment(segment) {
  if (!segment) return segment
  if (segment.includes('%')) return segment
  return segment.replace(/[^\x00-\x7F]/g, (char) => encodeURIComponent(char))
}

export function normalizeImageUrl(url) {
  if (!url || typeof url !== 'string') return ''

  let normalized = url.trim()
  for (const [pattern, replacement] of MOJIBAKE_REPLACEMENTS) {
    normalized = normalized.replace(pattern, replacement)
  }

  normalized = normalized.replace(/\uFFFD/g, '')

  try {
    const parsed = new URL(normalized)
    parsed.pathname = parsed.pathname
      .split('/')
      .map(encodePathSegment)
      .join('/')
    return parsed.toString()
  } catch {
    return normalized
  }
}

function extractFileName(url) {
  if (!url) return null

  const thumbMatch = url.match(/\/([^/?#]+\.(?:jpg|jpeg|png|webp|gif))(?:[/?#]|$)/i)
  if (thumbMatch) {
    return thumbMatch[1].replace(/\uFFFD/g, '')
  }

  return null
}

export function getImageCandidates(url) {
  if (!url || typeof url !== 'string') return []

  const candidates = []
  const normalized = normalizeImageUrl(url)
  if (normalized) candidates.push(normalized)

  const fileName = extractFileName(url)
  if (fileName) {
    const encodedName = encodeURIComponent(fileName)
    candidates.push(`https://commons.wikimedia.org/wiki/Special:FilePath/${encodedName}?width=320`)
  }

  if (url !== normalized && url.trim()) {
    candidates.push(url.trim())
  }

  return [...new Set(candidates.filter(Boolean))]
}

function wikiTitleFromImagelink(url) {
  if (!url || typeof url !== 'string') return null
  const match = url.match(/wikipedia\.org\/wiki\/([^#?]+)/i)
  if (!match) return null
  try {
    return decodeURIComponent(match[1].replace(/_/g, ' '))
  } catch {
    return match[1].replace(/_/g, ' ')
  }
}

function buildWikiTitles(placeName) {
  if (!placeName) return []
  return [
    placeName,
    `${placeName} de Bogotá`,
    `${placeName} de Colombia`,
    `${placeName} Bogotá`,
    `${placeName} Colombia`,
  ]
}

async function fetchWikiSummaryImage(title) {
  const slug = encodeURIComponent(title.replace(/ /g, '_'))

  for (const lang of ['es', 'en']) {
    try {
      const response = await fetch(
        `https://${lang}.wikipedia.org/api/rest_v1/page/summary/${slug}`
      )
      if (!response.ok) continue
      const data = await response.json()
      if (data.thumbnail?.source) return data.thumbnail.source
    } catch {
      // probar siguiente idioma
    }
  }

  return ''
}

async function searchWikiImage(query) {
  for (const lang of ['es', 'en']) {
    try {
      const params = new URLSearchParams({
        action: 'query',
        format: 'json',
        origin: '*',
        generator: 'search',
        gsrsearch: query,
        gsrlimit: '1',
        prop: 'pageimages',
        piprop: 'thumbnail',
        pithumbsize: '320',
      })
      const response = await fetch(
        `https://${lang}.wikipedia.org/w/api.php?${params.toString()}`
      )
      if (!response.ok) continue
      const data = await response.json()
      const pages = data?.query?.pages
      if (!pages) continue
      const page = Object.values(pages)[0]
      if (page?.thumbnail?.source) return page.thumbnail.source
    } catch {
      // probar siguiente idioma
    }
  }

  return ''
}

export async function fetchWikiImage(placeName, imagelink = '') {
  const titles = []
  const fromLink = wikiTitleFromImagelink(imagelink)
  if (fromLink) titles.push(fromLink)
  titles.push(...buildWikiTitles(placeName))

  const uniqueTitles = [...new Set(titles.filter(Boolean))]
  for (const title of uniqueTitles) {
    const image = await fetchWikiSummaryImage(title)
    if (image) return image
  }

  for (const query of uniqueTitles) {
    const image = await searchWikiImage(`${query} Bogotá Colombia`)
    if (image) return image
  }

  return ''
}
