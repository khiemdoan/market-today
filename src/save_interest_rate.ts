import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export interface Root {
  id: string;
  name: string;
  symbol: string;
  icon: string;
  interestRates: InterestRate[];
}

export interface InterestRate {
  deposit: number;
  value: number;
}


const DATA_DIR = path.join(__dirname, "..", "data");
const TERM_MONTHS = [0, 1, 3, 6, 9, 12, 18, 24];
const HEADERS = [
  "date",
  "bank",
  "no_fixed_term",
  "1_month",
  "3_months",
  "6_months",
  "9_months",
  "12_months",
  "18_months",
  "24_months",
];

const checkDirExist = (dir: string): void => {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
};

const buildKey = (date: string, bank: string): string =>
  `${date}|${bank}`;

const buildRateMap = (
  interestRates: InterestRate[] = []
): Map<number, number> => {
  return new Map(
    interestRates.map((r) => [r.deposit, r.value])
  );
};

const getRate = (
  rateMap: Map<number, number>,
  month: number
): number | string =>
  rateMap.get(month) ?? "N/A";


const readCSV = (filepath: string): string[] => {
  if (!fs.existsSync(filepath)) return [];

  const lines = fs.readFileSync(filepath, "utf8").trim().split("\n");
  lines.shift();
  return lines;
};

const writeCSV = (filepath: string, rows: string[]): void => {
  const content =
    [HEADERS.join(","), ...rows].join("\n") + "\n";
  fs.writeFileSync(filepath, content, "utf8");
};

const parseRowMeta = (row: string) => {
  const [date, bank] = row.split(",", 2);
  return {
    date,
    bank: bank.replace(/"/g, ""),
  };
};

const buildRow = (
  date: string,
  bank: string,
  interestRates: InterestRate[]
): string => {
  const rateMap = buildRateMap(interestRates);

  const values = TERM_MONTHS.map((m) =>
    getRate(rateMap, m)
  );

  return [date, `"${bank}"`, ...values].join(",");
};

const mergeRows = (
  existingRows: string[],
  newData: Root[],
  dateFormatted: string
): string[] => {
  const rowMap = new Map<string, string>();

  existingRows.forEach((row) => {
    const { date, bank } = parseRowMeta(row);
    rowMap.set(buildKey(date, bank), row);
  });

  newData.forEach((item) => {
    const key = buildKey(dateFormatted, item.name);
    const row = buildRow(
      dateFormatted,
      item.name,
      item.interestRates
    );
    rowMap.set(key, row);
  });

  return Array.from(rowMap.values());
};


export const saveInterestRate = (banks: Root[]): void | null => {
  if (!banks.length) return null;

  checkDirExist(DATA_DIR);

  const dateFormatted = new Date().toLocaleDateString("vi-VN");
  const filepath = path.join(DATA_DIR, "interest_rates.csv");

  const existingRows = readCSV(filepath);
  const rows = mergeRows(existingRows, banks, dateFormatted);

  writeCSV(filepath, rows);
};
