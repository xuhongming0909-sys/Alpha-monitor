const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const {
  enrichDiscountStrategyRow,
  buildConvertibleBondDiscountSnapshot,
} = require("../strategy/convertible_bond/service");
const {
  buildConvertibleBondDiscountMarkdown,
} = require("../notification/styles/discount_strategy_markdown");
const {
  buildSummaryMarkdown,
} = require("../notification/styles/markdown_style");
const {
  buildCbArbitrageMarkdown,
} = require("../notification/styles/cb_arbitrage_markdown");
const {
  createEventAlertService,
} = require("../notification/alerts/event_alert_service");
const {
  createCbArbitragePushService,
} = require("../notification/cb_arbitrage/service");
const {
  createConvertibleBondDiscountRuntimeStore,
} = require("../strategy/convertible_bond/discount_runtime_store");

function makeBaseRow(overrides = {}) {
  return {
    code: "113579",
    bondName: "健友转债",
    stockCode: "603707",
    stockName: "健友股份",
    price: 98,
    stockPrice: 10,
    convertPrice: 10,
    convertValue: 100,
    premiumRate: -2,
    stockAtr20: 1,
    remainingSizeYi: 5,
    stockMarketValueYi: 100,
    forceRedeemStatus: "不强赎",
    convertStartDate: "2024-01-01T00:00:00+08:00",
    ...overrides,
  };
}

test("enrichDiscountStrategyRow derives new ratios and retires old weighted-discount fields", () => {
  const row = enrichDiscountStrategyRow(makeBaseRow({
    atrRatio: 9.9,
    atrCoefficient: 1.2,
    sellPressureRatio: 0.3,
    sellPressureCoefficient: 0.4,
    boardCoefficient: 0.8,
    weightedDiscountRate: -3.1,
  }));

  assert.equal(row.bondToStockMarketValueRatio, 0.05);
  assert.equal(row.discountAtrRatio, 0.2);
  assert.equal(row.stockAtr20Pct, 10);
  assert.equal(row.forceRedeemLabel, "非强赎");
  assert.ok(!Object.prototype.hasOwnProperty.call(row, "atrRatio"));
  assert.ok(!Object.prototype.hasOwnProperty.call(row, "atrCoefficient"));
  assert.ok(!Object.prototype.hasOwnProperty.call(row, "sellPressureRatio"));
  assert.ok(!Object.prototype.hasOwnProperty.call(row, "sellPressureCoefficient"));
  assert.ok(!Object.prototype.hasOwnProperty.call(row, "boardCoefficient"));
  assert.ok(!Object.prototype.hasOwnProperty.call(row, "weightedDiscountRate"));
});

test("bootstrap snapshot emits buy signal immediately when current row already sits in buy zone", () => {
  const snapshot = buildConvertibleBondDiscountSnapshot(
    [makeBaseRow({ premiumRate: -2.3 })],
    {},
    {
      buyThreshold: -2,
      sellThreshold: -0.5,
      nowIsoText: "2026-04-22T09:30:00+08:00",
      todayDate: "2026-04-22",
    }
  );

  assert.equal(snapshot.isBootstrap, true);
  assert.equal(snapshot.buySignals.length, 1);
  assert.equal(snapshot.buySignals[0].code, "113579");
});

test("bootstrap state still allows a later same-day threshold crossing to emit one buy signal", () => {
  const first = buildConvertibleBondDiscountSnapshot(
    [makeBaseRow({ premiumRate: -1.9 })],
    {},
    {
      buyThreshold: -2,
      sellThreshold: -0.5,
      nowIsoText: "2026-04-22T09:30:00+08:00",
      todayDate: "2026-04-22",
    }
  );
  assert.equal(first.isBootstrap, true);
  assert.equal(first.buySignals.length, 0);

  const second = buildConvertibleBondDiscountSnapshot(
    [makeBaseRow({ premiumRate: -2.1 })],
    first.nextState,
    {
      buyThreshold: -2,
      sellThreshold: -0.5,
      nowIsoText: "2026-04-22T09:40:00+08:00",
      todayDate: "2026-04-22",
    }
  );

  assert.equal(second.isBootstrap, false);
  assert.equal(second.buySignals.length, 1);
  assert.equal(second.buySignals[0].bondToStockMarketValueRatio, 0.05);
  assert.ok(Math.abs(second.buySignals[0].discountAtrRatio - 0.21) < 1e-9);
});

test("event alert service does not swallow bootstrap buy signals", async () => {
  const sent = [];
  const runtimeState = {
    monitorPushRecords: {},
    getState() {
      return {};
    },
    replaceStrategyState() {},
    save() {},
    setBuySignalAttempt() {},
    setBuySignalSuccess() {},
    setBuySignalError() {},
    setSellSignalAttempt() {},
    setSellSignalSuccess() {},
    setSellSignalError() {},
    setMonitorPushAttempt() {},
    setMonitorPushSuccess() {},
    setMonitorPushError() {},
    getMonitorPushRecord() {
      return [];
    },
    setMonitorPushRecord() {},
  };
  const service = createEventAlertService({
    collectAlertDatasets: async () => ({ cbArb: { data: [makeBaseRow()] } }),
    buildDiscountSnapshot: () => ({
      isBootstrap: true,
      buySignals: [{
        code: "113579",
        bondName: "健友转债",
        premiumRate: -2.1,
        bondToStockMarketValueRatio: 0.05,
        discountAtrRatio: 2.1,
        forceRedeemLabel: "非强赎",
      }],
      sellSignals: [],
      premiumMonitorSummary: { count: 1, items: [] },
      nextState: {},
    }),
    buildDiscountMarkdown: (signalType, items) => `${signalType}:${items.length}`,
    sendMarkdown: async (markdown) => {
      sent.push(markdown);
      return { errcode: 0, errmsg: "ok" };
    },
    getDiscountStrategyConfig: () => ({
      tradingDaysOnly: true,
      sessionWindows: ["09:30-11:30", "13:00-15:00"],
      monitorSessionTimes: [],
      buyThreshold: -2,
      sellThreshold: -0.5,
    }),
    pushRuntimeStore: { save() {} },
    discountRuntimeStore: runtimeState,
    getShanghaiParts: () => ({ date: "2026-04-22", hour: 9, minute: 35, weekday: 3 }),
    isTradingSession: () => true,
    nowIso: () => "2026-04-22T09:35:00+08:00",
  });

  const result = await service.pushConvertibleBondAlerts();

  assert.equal(result.sent, true);
  assert.equal(sent.length, 1);
  assert.equal(sent[0], "buy:1");
});

test("event alert service retries bootstrap buy signal after a delivery failure", async () => {
  const delivered = [];
  const state = {};
  const runtimeStore = createConvertibleBondDiscountRuntimeStore({
    state,
    save() {},
  });
  let shouldFail = true;
  const service = createEventAlertService({
    collectAlertDatasets: async () => ({ cbArb: { data: [makeBaseRow({ premiumRate: -2.3 })] } }),
    buildDiscountSnapshot: buildConvertibleBondDiscountSnapshot,
    buildDiscountMarkdown: (signalType, items) => `${signalType}:${items.length}`,
    sendMarkdown: async (markdown) => {
      if (shouldFail) {
        shouldFail = false;
        throw new Error("wecom-temporary-down");
      }
      delivered.push(markdown);
      return { errcode: 0, errmsg: "ok" };
    },
    getDiscountStrategyConfig: () => ({
      tradingDaysOnly: true,
      sessionWindows: ["09:30-11:30", "13:00-15:00"],
      monitorSessionTimes: [],
      buyThreshold: -2,
      sellThreshold: -0.5,
    }),
    pushRuntimeStore: { save() {} },
    discountRuntimeStore: runtimeStore,
    getShanghaiParts: () => ({ date: "2026-04-22", hour: 9, minute: 35, weekday: 3 }),
    isTradingSession: () => true,
    nowIso: () => "2026-04-22T09:35:00+08:00",
  });

  await assert.rejects(
    () => service.pushConvertibleBondAlerts(),
    /wecom-temporary-down/
  );
  assert.equal(runtimeStore.getState().initializedDate, null);
  assert.deepEqual(runtimeStore.getState().signalStateMap, {});

  const second = await service.pushConvertibleBondAlerts();
  assert.equal(second.sent, true);
  assert.deepEqual(delivered, ["buy:1"]);
  assert.equal(runtimeStore.getState().initializedDate, "2026-04-22");
  assert.equal(runtimeStore.getState().signalStateMap["113579"].buyZoneActive, true);
});

test("discount markdown uses new metric fields and force-redeem wording", () => {
  const markdown = buildConvertibleBondDiscountMarkdown("monitor", [{
    code: "113579",
    bondName: "健友转债",
    premiumRate: -2.35,
    bondToStockMarketValueRatio: 0.08,
    discountAtrRatio: 1.52,
    forceRedeemActive: false,
  }], {
    generatedAtText: "2026-04-22 14:50:00",
  });

  assert.match(markdown, /转债市值比 8\.000%/);
  assert.match(markdown, /折价ATR比 152\.000%/);
  assert.match(markdown, /非强赎/);
  assert.doesNotMatch(markdown, /加权折价/);
  assert.doesNotMatch(markdown, /ATR系数/);
});

test("market value sources explicitly prefer float market value for cb arbitrage and rights issue", () => {
  const cbSourcePath = path.resolve(__dirname, "..", "data_fetch", "convertible_bond", "source.py");
  const cbSourceText = fs.readFileSync(cbSourcePath, "utf8");
  assert.match(cbSourceText, /"fields":\s*"f12,f21"/);
  assert.match(cbSourceText, /item\.get\("f21"\)/);
  assert.match(cbSourceText, /"流通市值"/);
  assert.doesNotMatch(cbSourceText, /for name in \("总市值", "总市值\(元\)", "market_value", "marketValue"\)/);

  const rightsIssueSourcePath = path.resolve(__dirname, "..", "data_fetch", "cb_rights_issue", "source.py");
  const rightsIssueSourceText = fs.readFileSync(rightsIssueSourcePath, "utf8");
  assert.match(rightsIssueSourceText, /"fields":\s*"f12,f21"/);
  assert.match(rightsIssueSourceText, /item\.get\("f21"\)/);
  assert.match(rightsIssueSourceText, /"流通市值"/);
  assert.doesNotMatch(rightsIssueSourceText, /for name in \("总市值", "总市值\(元\)", "market_value", "marketValue"\)/);
});

test("summary markdown ignores legacy cbArb module after independent push split", () => {
  const markdown = buildSummaryMarkdown({
    ipo: { data: [{ code: "301000", name: "测试新股", subscribeDate: "2026-04-22" }] },
    bonds: { data: [{ code: "113000", name: "测试转债", subscribeDate: "2026-04-22" }] },
    cbArb: { data: [makeBaseRow({ theoreticalPremiumRate: 5, doubleLow: 120 })] },
    monitors: [{ name: "示例监控", stockYieldRate: 1.234, cashYieldRate: 0.456 }],
    ah: { data: [{ aName: "AH样本", aCode: "600000", premium: 10, percentile: 90, aPrice: 10, hPriceCny: 11 }] },
    ab: { data: [{ aName: "AB样本", aCode: "900000", premium: -5, percentile: 10, aPrice: 10, bPriceCny: 9.5 }] },
    eventArbNextDaySummary: [{ name: "不应出现", symbol: "600001", eventType: "事件", eventStage: "阶段" }],
  }, {
    subscription: true,
    cbArb: true,
    monitor: true,
    ahab: true,
    dividend: true,
    eventArb: true,
  }, {
    generatedAtText: "2026-04-22 14:50:00",
    todayText: "2026-04-22",
    summaryConfig: { ahTopN: 1, abTopN: 1, cbTopN: 3 },
    todayDividendRecord: [{ name: "不应出现", code: "600002", dividendData: { recordDate: "2026-04-22" } }],
  });

  const order = [
    markdown.indexOf("**今日打新**"),
    markdown.indexOf("**自定义监控**"),
    markdown.indexOf("**AH**"),
    markdown.indexOf("**AB**"),
  ];
  assert.ok(order.every((value) => value >= 0));
  assert.deepEqual([...order].sort((a, b) => a - b), order);
  assert.equal(markdown.includes("113579"), false);
  assert.equal(markdown.includes("可转债套利"), false);
  assert.equal(markdown.includes("分红提醒"), false);
  assert.equal(markdown.includes("事件套利"), false);
});

test("cb arbitrage markdown pushes total annualized yield for small redemption rows", () => {
  const markdown = buildCbArbitrageMarkdown({
    updateTime: "2026-04-23 14:30:00",
    rows: [
      makeBaseRow({
        bondName: "闻泰转债",
        price: 98,
        premiumRate: 8,
        doubleLow: 106,
        pureBondValue: 92,
        theoreticalPrice: 101,
        theoreticalPremiumRate: 4,
        isSmallRedemption: true,
        remainingYears: 1,
        totalAnnualizedYield: 0.152,
        redemptionAmount: 225641.88,
        liabilityExposureYi: 18.68,
      }),
    ],
  });

  assert.match(markdown, /闻泰转债 98元/);
  assert.match(markdown, /转股溢价率：\+8%/);
  assert.match(markdown, /总年化收益率：\+15\.2%/);
  assert.doesNotMatch(markdown, /刚兑收益率/);
  assert.match(markdown, /预期耗时：1\.5年（剩余期限：1年）/);
  assert.match(markdown, /刚兑金额：225641\.88元/);
  assert.match(markdown, /负债敞口：18\.68亿/);
});

test("cb arbitrage push service dedupes main and small redemption candidates", async () => {
  const service = createCbArbitragePushService({
    runtimeStore: {},
    getDataset: async () => ({
      data: [
        makeBaseRow({
          code: "113579",
          bondName: "闻泰转债",
          doubleLow: 106,
          theoreticalPremiumRate: 4,
        }),
      ],
      summary: {
        topDoubleLow: [makeBaseRow({ code: "113579", bondName: "闻泰转债", doubleLow: 106 })],
      },
      smallRedemption: {
        rows: [
          makeBaseRow({
            code: "113579",
            bondName: "闻泰转债",
            expectedDurationYears: 1.5,
            redemptionAmount: 500000,
            liabilityExposureYi: 11.2,
            totalAnnualizedYield: 0.188,
          }),
          makeBaseRow({ code: "128001", bondName: "龙大转债", price: 85 }),
        ],
      },
    }),
  });

  const payload = await service.readPayload();

  assert.deepEqual(payload.rows.map((row) => row.code), ["113579", "128001"]);
  assert.equal(payload.rows[0].isSmallRedemption, true);
  assert.equal(payload.rows[0].theoreticalPremiumRate, 4);
  assert.equal(payload.rows[0].redemptionAmount, 500000);
  assert.equal(payload.rows[0].liabilityExposureYi, 11.2);
  assert.equal(payload.rows[0].totalAnnualizedYield, 0.188);
});

test("small redemption formulas expose option annualized and total annualized yields", () => {
  const cbSourcePath = path.resolve(__dirname, "..", "data_fetch", "convertible_bond", "source.py");
  const cbSourceText = fs.readFileSync(cbSourcePath, "utf8");

  assert.match(cbSourceText, /smallRedemptionOptionYield/);
  assert.match(cbSourceText, /smallRedemptionOptionAnnualizedYield/);
  assert.match(cbSourceText, /smallRedemptionTotalAnnualizedYield/);
  assert.match(cbSourceText, /option_yield = option_value \/ market_price/);
  assert.match(cbSourceText, /total_annualized_yield = redemption_annualized_yield \+ option_annualized_yield/);
});

test("config contract includes cb_discount_strategy_state runtime file and retires old factor config", () => {
  const configPath = path.resolve(__dirname, "..", "config.yaml");
  const configText = fs.readFileSync(configPath, "utf8");

  assert.match(configText, /cb_discount_strategy_state:\s*"cb_discount_strategy_state\.json"/);
  assert.doesNotMatch(configText, /\batr_anchor_points:/);
  assert.doesNotMatch(configText, /\bsell_pressure_anchor_points:/);
  assert.doesNotMatch(configText, /\bboard_coefficients:/);
});

test("requirements include pdf parsing dependencies for convertible bond holder extraction", () => {
  const requirementsPath = path.resolve(__dirname, "..", "requirements.txt");
  const requirementsText = fs.readFileSync(requirementsPath, "utf8");

  assert.match(requirementsText, /^pdfminer\.six$/m);
  assert.match(requirementsText, /^pypdf$/m);
});
