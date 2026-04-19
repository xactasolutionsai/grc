/**
 * Client helper for calling local AI (Ollama) endpoints through the SvelteKit
 * proxy at /fe-api/ai/<path>. The backend returns a uniform envelope:
 *
 *   { data: T | null, raw: string | null, parse_error: boolean }
 *
 * `callAI` unwraps it and throws a typed `AIClientError` on failure so callers
 * can display a toast and keep the button re-usable.
 */

export type AIEnvelope<T> = {
	data: T | null;
	raw: string | null;
	parse_error: boolean;
};

export class AIClientError extends Error {
	status: number;
	code: 'service_unavailable' | 'parse_error' | 'bad_request' | 'unknown';

	constructor(
		message: string,
		status: number,
		code: AIClientError['code']
	) {
		super(message);
		this.status = status;
		this.code = code;
	}
}

export async function callAI<T>(
	path: string,
	body: unknown = {},
	fetchFn: typeof fetch = fetch
): Promise<T> {
	const res = await fetchFn(`/fe-api/ai/${path}`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(body ?? {})
	});

	if (res.status === 503) {
		throw new AIClientError(
			'AI service is unavailable. Make sure Ollama is running.',
			503,
			'service_unavailable'
		);
	}
	if (res.status === 400) {
		let msg = 'Invalid input for AI request.';
		try {
			const j = await res.json();
			msg = typeof j === 'string' ? j : JSON.stringify(j);
		} catch {
			/* ignore */
		}
		throw new AIClientError(msg, 400, 'bad_request');
	}
	if (!res.ok) {
		throw new AIClientError(`AI request failed (HTTP ${res.status}).`, res.status, 'unknown');
	}

	const envelope = (await res.json()) as AIEnvelope<T>;
	if (envelope.parse_error || envelope.data == null) {
		throw new AIClientError(
			'The AI model did not return structured output. Please retry.',
			200,
			'parse_error'
		);
	}
	return envelope.data;
}

// Typed payload shapes matching backend/ai/prompts.py
export type AnalyzeRiskResult = {
	description: string;
	threat_scenario: string;
	impact: string;
	likelihood: { level: 'Low' | 'Medium' | 'High'; justification: string };
	risk_level: 'Low' | 'Medium' | 'High' | 'Critical';
	recommended_mitigations: string[];
	security_domains: string[];
};

export type ExpandTextResult = { expanded: string };

export type GeneratedControl = {
	name: string;
	description: string;
	implementation_guidance: string;
	control_type: 'preventive' | 'detective' | 'corrective' | 'deterrent' | 'compensating';
};

export type GenerateControlsResult = { controls: GeneratedControl[] };

export type GenerateFindingResult = {
	title: string;
	description: string;
	impact: string;
	recommendation: string;
	severity: 'low' | 'medium' | 'high' | 'critical';
};

export type DashboardInsightsResult = {
	top_risks: string[];
	compliance_gaps: string[];
	recommended_actions: string[];
	summary: string;
};
