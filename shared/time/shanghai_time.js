"use strict";

/**
 * 上海时区时间工具。
 * 这里统一处理交易日、交易时段、日期标准化和截止时间判断。
 */

const SHANGHAI_TIMEZONE = "Asia/Shanghai";

function nowIso() {
  return new Date().toISOString();
}

function getShanghaiParts(date = new Date()) {
  const formatter = new Intl.DateTimeFormat("en-CA", {
    timeZone: SHANGHAI_TIMEZONE,
    hour12: false,
    hourCycle: "h23",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    weekday: "short",
  });
  const parts = Object.fromEntries(formatter.formatToParts(date).map((item) => [item.type, item.value]));
  const weekdayMap = { Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6, Sun: 0 };
  const rawHour = Number(parts.hour || 0);
  // 部分 Node/ICU 运行环境会把上海时间午夜格式化成 24:xx，这里统一归一成 00:xx。
  const normalizedHour = rawHour === 24 ? 0 : rawHour;

  return {
    date: `${parts.year}-${parts.month}-${parts.day}`,
    hour: normalizedHour,
    minute: Number(parts.minute || 0),
    second: Number(parts.second || 0),
    weekday: weekdayMap[parts.weekday] ?? -1,
  };
}

function normalizeDateText(value) {
  const text = String(value || "").trim();
  if (!text) return "";
  const hit = text.match(/\d{4}-\d{2}-\d{2}/);
  return hit ? hit[0] : text.slice(0, 10);
}

function parseTimeToMinutes(timeText) {
  const hit = String(timeText || "").trim().match(/^(\d{2}):(\d{2})$/);
  if (!hit) return null;
  const hour = Number(hit[1]);
  const minute = Number(hit[2]);
  if (!Number.isFinite(hour) || !Number.isFinite(minute)) return null;
  if (hour < 0 || hour > 23 || minute < 0 || minute > 59) return null;
  return hour * 60 + minute;
}

function isTradingWeekday(date = new Date()) {
  const parts = getShanghaiParts(date);
  return parts.weekday >= 1 && parts.weekday <= 5;
}

function isTradingSession(date = new Date()) {
  const parts = getShanghaiParts(date);
  if (parts.weekday < 1 || parts.weekday > 5) return false;
  const minutes = parts.hour * 60 + parts.minute;
  const inWindow = (startHour, startMinute, endHour, endMinute) => {
    const start = startHour * 60 + startMinute;
    const end = endHour * 60 + endMinute;
    return minutes >= start && minutes <= end;
  };

  return (
    inWindow(9, 30, 11, 30) ||
    inWindow(13, 0, 15, 0) ||
    inWindow(9, 30, 12, 0) ||
    inWindow(13, 0, 16, 0)
  );
}

function isAfterCutoff(date = new Date(), cutoffTime = "16:10") {
  const parts = getShanghaiParts(date);
  if (parts.weekday < 1 || parts.weekday > 5) return false;
  const cutoffMinutes = parseTimeToMinutes(cutoffTime);
  if (cutoffMinutes === null) return false;
  return parts.hour * 60 + parts.minute >= cutoffMinutes;
}

module.exports = {
  SHANGHAI_TIMEZONE,
  nowIso,
  getShanghaiParts,
  normalizeDateText,
  parseTimeToMinutes,
  isTradingWeekday,
  isTradingSession,
  isAfterCutoff,
};
