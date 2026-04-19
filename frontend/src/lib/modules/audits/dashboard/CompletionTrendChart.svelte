<script lang="ts">
	import { onMount } from 'svelte';
	import * as echarts from 'echarts';

	interface TrendData {
		month: string;
		completed: number;
		planned: number;
		completion_rate: number;
	}

	interface Props {
		data?: TrendData[];
	}

	let { data = [] }: Props = $props();
	let chartContainer: HTMLDivElement;
	let myChart: echarts.ECharts;

	onMount(() => {
		if (data && data.length > 0) {
			renderChart();
		}

		return () => {
			if (myChart) {
				myChart.dispose();
			}
		};
	});

	$effect(() => {
		if (data && chartContainer) {
			renderChart();
		}
	});

	function renderChart() {
		if (!chartContainer) return;

		if (myChart) {
			myChart.dispose();
		}

		myChart = echarts.init(chartContainer);

		const option = {
			tooltip: {
				trigger: 'axis',
				axisPointer: {
					type: 'cross'
				}
			},
			legend: {
				data: ['Completed', 'Planned', 'Completion Rate'],
				bottom: 0
			},
			grid: {
				left: '3%',
				right: '4%',
				bottom: '15%',
				containLabel: true
			},
			xAxis: {
				type: 'category',
				data: data.map(d => d.month),
				axisLabel: {
					rotate: 45
				}
			},
			yAxis: [
				{
					type: 'value',
					name: 'Count',
					position: 'left'
				},
				{
					type: 'value',
					name: 'Rate (%)',
					position: 'right',
					min: 0,
					max: 100
				}
			],
			series: [
				{
					name: 'Completed',
					type: 'bar',
					data: data.map(d => d.completed),
					itemStyle: {
						color: '#10b981'
					}
				},
				{
					name: 'Planned',
					type: 'bar',
					data: data.map(d => d.planned),
					itemStyle: {
						color: '#3b82f6'
					}
				},
				{
					name: 'Completion Rate',
					type: 'line',
					yAxisIndex: 1,
					data: data.map(d => d.completion_rate.toFixed(1)),
					itemStyle: {
						color: '#f59e0b'
					},
					lineStyle: {
						width: 3
					}
				}
			]
		};

		myChart.setOption(option);

		// Responsive
		window.addEventListener('resize', () => myChart.resize());
	}
</script>

<div bind:this={chartContainer} class="w-full h-full"></div>
