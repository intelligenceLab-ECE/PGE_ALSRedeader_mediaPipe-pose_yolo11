export function cn(...items: Array<string | undefined | false>): string {
  return items.filter(Boolean).join(" " );
}
