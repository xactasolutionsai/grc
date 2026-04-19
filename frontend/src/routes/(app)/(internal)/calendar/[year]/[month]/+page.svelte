<script lang="ts">
	import { page } from '$app/state';
	import Calendar from '$lib/components/Calendar/Calendar.svelte';
	import type { PageData } from './$types';

	interface Props {
		data: PageData;
	}

	let { data }: Props = $props();

	let year = $derived(parseInt(page.params.year));
	let month = $derived(parseInt(page.params.month));

	function createCalendarEvents(
		appliedControls: Record<string, string>[],
		riskAcceptances: Record<string, string>[],
		tasks: Record<string, string>[],
		auditEntities: Record<string, string>[],
		auditPlans: Record<string, string>[]
	): Array<{ label: string; date: Date; link: string }> {
		const events = [
			...appliedControls.map((control: Record<string, string>) => ({
				label: `AC: ${control.name}`,
				date: new Date(control.eta),
				link: `/applied-controls/${control.id}`,
				users: control.owner,
				color: 'tertiary'
			})),
			...riskAcceptances.map((ra: Record<string, string>) => ({
				label: `RA: ${ra.name}`,
				date: new Date(ra.expiry_date),
				link: `/risk-acceptances/${ra.id}`,
				users: ra.approver ? [ra.approver] : [],
				color: 'secondary'
			})),
			...tasks.map((task: Record<string, any>) => ({
				label: `TA: ${task.name}`,
				date: new Date(task.due_date),
				link: !task.is_recurrent
					? `/task-templates/${task.task_template?.id || task.id}`
					: `/task-nodes/${task.id}`,
				users: task.assigned_to,
				color: 'primary'
			})),
			...auditEntities.map((entity: Record<string, any>) => ({
				label: `AU: ${entity.name}`,
				date: new Date(entity.next_audit_date),
				link: `/audits/universe/${entity.id}`,
				users: entity.owner ? [entity.owner] : [],
				color: getEntityTypeColor(entity.entity_type)
			})),
			...auditPlans.map((plan: Record<string, any>) => ({
				label: `AP: ${plan.title}`,
				date: new Date(plan.planned_start),
				link: `/audits/planning/${plan.id}`,
				users: plan.lead_auditor ? [plan.lead_auditor] : [],
				color: getPlanStatusColor(plan.status)
			}))
		];
		return events;
	}

	function getEntityTypeColor(entityType: string): string {
		const colorMap: Record<string, string> = {
			'business_unit': 'success',
			'process': 'warning',
			'system': 'error',
			'vendor': 'surface',
			'compliance_domain': 'primary'
		};
		return colorMap[entityType] || 'surface';
	}

	function getPlanStatusColor(status: string): string {
		const colorMap: Record<string, string> = {
			'planned': 'tertiary',
			'in_progress': 'warning',
			'completed': 'success',
			'cancelled': 'error'
		};
		return colorMap[status] || 'surface';
	}

	let info = $derived(createCalendarEvents(data.appliedControls, data.riskAcceptances, data.tasks, data.auditEntities, data.auditPlans));
</script>

<Calendar {info} {year} {month} />
