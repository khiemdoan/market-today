import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import pl, { DataFrame } from "nodejs-polars";

interface BankRecord {
    id: string;
    name: string;
    symbol: string;
    icon: string;
    interestRates: InterestRate[];
}
interface InterestRate {
    deposit: number;
    value: number;
}

const FILE_NAME = fileURLToPath(import.meta.url);
const DIR_NAME = path.dirname(FILE_NAME);
const DATA_DIR = path.join(DIR_NAME, "..", "data");
const FILE_PATH = path.join(DATA_DIR, "interest_rates.csv");
const MONTH_KEY = {
    0: "no_fixed_term",
    1: "1_month",
    3: "3_months",
    6: "6_months",
    9: "9_months",
    12: "12_months",
    18: "18_months",
    24: "24_months",
};

const MONTHS = Object.keys(MONTH_KEY).map(Number);

const checkDirExist = () => {
    if (!fs.existsSync(DATA_DIR)) {
        fs.mkdirSync(DATA_DIR, { recursive: true });
    }
};

const readExistingCsv = async (): Promise<DataFrame> => {
    let df = pl.DataFrame([]);
    if (!fs.existsSync(FILE_PATH)) return df;
    df = await pl.readCSV(FILE_PATH, {
        hasHeader: true,
        dtypes: {
            date: pl.Utf8,
            bank: pl.Utf8,
            no_fixed_term: pl.Float64,
            "1_month": pl.Float64,
            "3_months": pl.Float64,
            "6_months": pl.Float64,
            "9_months": pl.Float64,
            "12_months": pl.Float64,
            "18_months": pl.Float64,
            "24_months": pl.Float64,
        },
    });
    return df;
};

const transformBankRecordsToRows = (banks: BankRecord[], date: string) => {
    const transformOneBank = (bank: BankRecord) => {
        const row: Record<string, string | number | null> = {
            date,
            bank: bank.name,
        };

        for (const term of MONTHS) {
            const key = MONTH_KEY[term as keyof typeof MONTH_KEY];
            row[key] =
                bank.interestRates.find((r) => r.deposit === term)?.value ??
                null;
        }
        return row;
    };

    return banks.map(transformOneBank);
};

export const saveInterestRate = async (banks: BankRecord[]) => {
    if (!banks.length) return;
    checkDirExist();

    const date = new Date().toISOString().slice(0, 10);
    const oldDf = await readExistingCsv();
    const newDf = pl.DataFrame(transformBankRecordsToRows(banks, date));

    const finalDf = pl
        .concat([oldDf, newDf])
        .unique({ subset: ["date", "bank"], keep: "last" });

    await finalDf.writeCSV(FILE_PATH);
};
