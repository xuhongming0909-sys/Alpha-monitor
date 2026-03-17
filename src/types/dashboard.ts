export interface OpportunityItem {
  name: string;
  code: string;
  premium: number | null;
}

export interface SubscriptionItem {
  name: string;
  code: string;
  date: string;
  category: 'IPO' | 'Bond';
}

export interface ArbitrageMonitorItem {
  name: string;
  stockYieldRate: number | null;
  cashYieldRate: number | null;
  maxYieldRate: number | null;
  note?: string;
}

export interface DividendItem {
  code: string;
  name: string;
  dividendYield: number | null;
  exDividendDate: string | null;
  payDate: string | null;
}

export interface MessageItem {
  userId: string;
  content: string;
  time: string;
}

export interface DashboardData {
  generatedAt: string;
  goal: string;
  implementationPath: string[];
  ahTopPremium: OpportunityItem[];
  abLowPremium: OpportunityItem[];
  upcomingSubscriptions: SubscriptionItem[];
  arbitrageMonitors: ArbitrageMonitorItem[];
  dividendPortfolio: DividendItem[];
  messages: MessageItem[];
}
