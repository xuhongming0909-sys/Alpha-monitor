import React, { useEffect, useState } from 'react';
import {
  ActivityIndicator,
  RefreshControl,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { fetchDashboardData } from '../services/dashboardApi';
import type { DashboardData } from '../types/dashboard';

function formatPercent(value: number | null): string {
  if (value === null) return '--';
  const sign = value > 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
}

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <View style={styles.card}>
      <Text style={styles.cardTitle}>{title}</Text>
      {children}
    </View>
  );
}

export default function HomeScreen() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      setError(null);
      const next = await fetchDashboardData();
      setData(next);
    } catch (e) {
      setError(e instanceof Error ? e.message : '加载失败');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (loading) {
    return (
      <SafeAreaView style={styles.center}>
        <ActivityIndicator size='large' color='#0f172a' />
        <Text style={styles.tip}>正在加载你的私有看板...</Text>
      </SafeAreaView>
    );
  }

  if (error || !data) {
    return (
      <SafeAreaView style={styles.center}>
        <Text style={styles.errorTitle}>加载失败</Text>
        <Text style={styles.tip}>{error ?? '没有拿到数据'}</Text>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} />}
      >
        <Text style={styles.title}>Alpha Monitor</Text>
        <Text style={styles.subtitle}>{data.goal}</Text>

        <SectionCard title='AH 高溢价'>
          {data.ahTopPremium.map((item) => (
            <View style={styles.row} key={item.code}>
              <Text style={styles.name}>{item.name} ({item.code})</Text>
              <Text style={styles.value}>{formatPercent(item.premium)}</Text>
            </View>
          ))}
        </SectionCard>

        <SectionCard title='AB 低溢价'>
          {data.abLowPremium.map((item) => (
            <View style={styles.row} key={item.code}>
              <Text style={styles.name}>{item.name} ({item.code})</Text>
              <Text style={styles.value}>{formatPercent(item.premium)}</Text>
            </View>
          ))}
        </SectionCard>

        <SectionCard title='套利监控'>
          {data.arbitrageMonitors.map((item, idx) => (
            <View style={styles.row} key={`${item.name}-${idx}`}>
              <Text style={styles.name}>{item.name}</Text>
              <Text style={styles.value}>{formatPercent(item.maxYieldRate)}</Text>
            </View>
          ))}
        </SectionCard>

        <SectionCard title='分红持仓'>
          {data.dividendPortfolio.map((item) => (
            <View style={styles.row} key={item.code}>
              <Text style={styles.name}>{item.name} ({item.code})</Text>
              <Text style={styles.value}>{formatPercent(item.dividendYield)}</Text>
            </View>
          ))}
        </SectionCard>

        <SectionCard title='近期提醒'>
          {data.upcomingSubscriptions.length === 0 ? (
            <Text style={styles.tip}>暂无提醒</Text>
          ) : (
            data.upcomingSubscriptions.map((item) => (
              <View style={styles.row} key={`${item.code}-${item.date}`}>
                <Text style={styles.name}>{item.name} ({item.code})</Text>
                <Text style={styles.value}>{item.date}</Text>
              </View>
            ))
          )}
        </SectionCard>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8fafc' },
  content: { padding: 16, gap: 12 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#f8fafc' },
  title: { fontSize: 30, fontWeight: '700', color: '#0f172a' },
  subtitle: { fontSize: 14, color: '#475569', marginBottom: 6 },
  card: { backgroundColor: '#fff', borderRadius: 14, borderWidth: 1, borderColor: '#e2e8f0', padding: 14, gap: 8 },
  cardTitle: { fontSize: 18, fontWeight: '600', color: '#0f172a', marginBottom: 4 },
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', gap: 10 },
  name: { fontSize: 14, color: '#0f172a', flex: 1 },
  value: { fontSize: 13, color: '#334155' },
  tip: { marginTop: 8, color: '#64748b' },
  errorTitle: { fontSize: 20, fontWeight: '700', color: '#b91c1c' },
});
