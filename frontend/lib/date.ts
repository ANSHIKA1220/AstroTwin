export function localISODate(value = new Date()): string {
  const year = value.getFullYear();
  const month = String(value.getMonth() + 1).padStart(2, "0");
  const day = String(value.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

export function futureISODate(days = 1): string {
  const value = new Date();
  value.setHours(12, 0, 0, 0);
  value.setDate(value.getDate() + days);
  return localISODate(value);
}

export function dateFromISO(value: string): Date {
  return new Date(`${value.slice(0, 10)}T12:00:00`);
}

export function daysFromToday(value: string): number {
  const target = dateFromISO(value);
  const today = new Date();
  today.setHours(12, 0, 0, 0);
  return Math.round((target.getTime() - today.getTime()) / 86_400_000);
}

export function fullDateLabel(value = new Date()): string {
  return value.toLocaleDateString("en-IN", { weekday: "long", day: "numeric", month: "long" });
}

export function greeting(value = new Date()): string {
  const hour = value.getHours();
  if (hour < 12) return "Good morning";
  if (hour < 17) return "Good afternoon";
  return "Good evening";
}
