import { test, expect } from '../utils/test-utils.js';

/**
 * Smoke test for the Analyze Risk flow. We mock the backend AI proxy
 * (`/fe-api/ai/analyze-risk`) so this test does not require a running
 * Ollama instance.
 */
test('Risk AI Assistant fills description and shows suggestions (mocked)', async ({
	logedPage,
	pages,
	sideBar,
	page
}) => {
	await page.route('**/fe-api/ai/analyze-risk', async (route) => {
		await route.fulfill({
			status: 200,
			contentType: 'application/json',
			body: JSON.stringify({
				data: {
					description: 'A deliberate threat actor encrypts HR data for ransom.',
					threat_scenario: 'Spear-phishing email delivers ransomware payload.',
					impact: 'Business interruption and potential data loss.',
					likelihood: { level: 'High', justification: 'Frequent phishing attempts observed.' },
					risk_level: 'High',
					recommended_mitigations: ['Enforce MFA', 'Segment HR VLAN'],
					security_domains: ['Identity & Access', 'Email Security']
				},
				raw: null,
				parse_error: false
			})
		});
	});

	await sideBar.click('Risk', pages.riskScenariosPage.url);
	await pages.riskScenariosPage.hasUrl();

	// Open the create modal via the generic add button.
	await page.getByTestId('add-button').click();

	// Fill the required name field.
	await page.getByLabel(/Name/i).first().fill('Ransomware on HR server');

	// Click the AI assist button that sits in the scenario form.
	await page.getByTestId('ai-assist-button').first().click();

	// Suggestions panel appears and description field is filled from the AI.
	const suggestionsPanel = page.getByTestId('ai-suggestions-panel');
	await expect(suggestionsPanel).toBeVisible();
	await expect(suggestionsPanel).toContainText('High');
	await expect(suggestionsPanel).toContainText('Enforce MFA');

	// The description (markdown editor textarea) should have been populated.
	const description = page.locator('textarea').first();
	await expect(description).toContainText(/ransom/i);
});
