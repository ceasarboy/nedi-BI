export const colorSchemes = {
  default: {
    colors: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#fc8452', '#9a60b4', '#ea7ccc']
  },
  blue: {
    colors: ['#3b82f6', '#60a5fa', '#2563eb', '#1d4ed8', '#1e40af', '#3730a3', '#6366f1', '#8b5cf6', '#a78bfa']
  },
  green: {
    colors: ['#10b981', '#34d399', '#059669', '#047857', '#065f46', '#064e3b', '#84cc16', '#a3e635', '#bef264']
  },
  purple: {
    colors: ['#8b5cf6', '#a78bfa', '#7c3aed', '#6d28d9', '#5b21b6', '#4c1d95', '#ec4899', '#f472b6', '#f9a8d4']
  },
  orange: {
    colors: ['#f59e0b', '#fbbf24', '#d97706', '#b45309', '#92400e', '#78350f', '#ef4444', '#f87171', '#fca5a5']
  },
  red: {
    colors: ['#ef4444', '#f87171', '#dc2626', '#b91c1c', '#991b1b', '#7f1d1d', '#f97316', '#fb923c', '#fdba74']
  },
  cyan: {
    colors: ['#06b6d4', '#22d3ee', '#0891b2', '#0e7490', '#155e75', '#164e63', '#14b8a6', '#2dd4bf', '#5eead4']
  },
  pink: {
    colors: ['#ec4899', '#f472b6', '#db2777', '#be185d', '#9d174d', '#831843', '#f59e0b', '#fbbf24', '#fcd34d']
  },
  yellow: {
    colors: ['#eab308', '#facc15', '#ca8a04', '#a16207', '#854d0e', '#713f12', '#f97316', '#fb923c', '#fdba74']
  },
  warm: {
    colors: ['#ff6b6b', '#ffa07a', '#ffd93d', '#ff9a76', '#ff6347', '#ff7f50', '#ffa500', '#ff8c00', '#ff4500']
  },
  cool: {
    colors: ['#6495ed', '#4682b4', '#4169e1', '#00bfff', '#1e90ff', '#00ced1', '#008b8b', '#20b2aa', '#5f9ea0']
  },
  vintage: {
    colors: ['#d87c7c', '#919e8b', '#d7ab82', '#6e7074', '#61a0a8', '#efa18d', '#787464', '#cc7e63', '#724e58']
  },
  rainbow: {
    colors: ['#ef4444', '#f59e0b', '#eab308', '#10b981', '#06b6d4', '#3b82f6', '#8b5cf6', '#ec4899']
  }
}

export function getColorScheme(schemeName) {
  return colorSchemes[schemeName] || colorSchemes.default
}

export function getColorList(schemeName) {
  return getColorScheme(schemeName).colors
}

export function getSingleColor(schemeName, index = 0) {
  const colors = getColorList(schemeName)
  return colors[index % colors.length]
}
