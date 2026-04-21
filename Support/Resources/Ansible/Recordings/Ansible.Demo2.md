Shot 1
Duration: 0:00 to 0:08
Things to record: Title frame, Demo 2 heading
On-screen text: Demo 2: Site Network Settings and Device Credentials
Script: In Demo 2, we establish the operational baseline by applying site policy first, then device access credentials.

Shot 2
Duration: 0:08 to 0:22
Things to record: settings.json, cropped to network_settings and device_credentials blocks
On-screen text: Single source of truth
Script: Both playbooks read this same data source, so policy and credentials are aligned per site.
Capture note: Blur secrets and passwords.

Shot 3
Duration: 0:22 to 0:34
Things to record: Catalyst Center Design Network Settings page for Global/PODS/POD 0/Building P0/Floor 1 before-state
On-screen text: Before state
Script: This is the current site settings state before automation.

Shot 4
Duration: 0:34 to 0:44
Things to record: Quick code credibility shot in network_settings.yml
On-screen text: Resolve site, apply composite settings payload
Script: Playbook 2.0 resolves site IDs and pushes DNS, NTP, syslog, SNMP, banner, and AAA settings in one flow.

Shot 5
Duration: 0:44 to 0:52
Things to record: Terminal in 2.0 directory, command execution
Command to show: ansible-playbook network_settings.yml --vault-password-file .vault_pass
On-screen text: Execute 2.0
Script: Now I run playbook 2.0 to apply network settings per site.

Shot 6
Duration: 0:52 to 1:16
Things to record: Terminal output from 2.0
Keep visible lines: site UUID resolution, PUT network request, execution status polling, SUCCESS
On-screen text: Async apply with status polling
Script: You can see site resolution, settings submission, and async polling until Catalyst Center reports success.

Shot 7
Duration: 1:16 to 1:30
Things to record: Catalyst Center Network Settings after-state with updated values
On-screen text: Site policy applied
Script: The site-level operational policy is now converged to the desired state.

Shot 8
Duration: 1:30 to 1:40
Things to record: Quick code credibility shot in credentials.yml
On-screen text: Create or update credentials, assign to site
Script: Next is playbook 3.0, which manages CLI, SNMP, and NETCONF credentials and assignment.

Shot 9
Duration: 1:40 to 1:48
Things to record: Terminal in 3.0 directory, command execution
Command to show: ansible-playbook credentials.yml --vault-password-file .vault_pass
On-screen text: Execute 3.0
Script: I now run playbook 3.0 to configure credentials and bind them to the site.

Shot 10
Duration: 1:48 to 2:18
Things to record: Terminal output from 3.0
Keep visible lines: workflow manager merged state, credential creation or update, assignment to site, completion summary
On-screen text: Credential lifecycle + assignment
Script: This run converges credential state and ensures Catalyst Center can authenticate to devices at this site.

Shot 11
Duration: 2:18 to 2:36
Things to record: Catalyst Center Credentials view and assignment evidence
On-screen text: Credentials present and assigned
Script: Here we can confirm credentials exist and are assigned, which is required for reliable discovery and management.

Shot 12
Duration: 2:36 to 2:55
Things to record: Quick idempotency proof, rerun both playbooks or one representative rerun
Commands to show:
ansible-playbook network_settings.yml --vault-password-file .vault_pass
ansible-playbook credentials.yml --vault-password-file .vault_pass
On-screen text: Safe to re-run
Script: On re-run, both playbooks converge rather than creating duplicate operational objects.

Shot 13
Duration: 2:55 to 3:10
Things to record: Split final state, Network Settings plus Credentials
On-screen text: Policy context + auth context ready
Script: At this point, the site has both policy context and authentication context, which prepares us for device discovery.

Shot 14
Duration: 3:10 to 3:20
Things to record: Closing frame
On-screen text:

Site settings converged
Device credentials converged
Ready for Demo 3 Discovery
Script: Demo 2 completes the baseline needed to discover and assign devices cleanly in the next stage.
Best capture list for Demo 2

settings.json crop with only network_settings and device_credentials in settings.json
Network Settings before and after in Catalyst Center
2.0 run with execution-status success
Credentials view and assignment evidence after 3.0
Short rerun proof showing convergence behavior
Trim out

Long idle waits during polling
Noisy debug blocks with no decision value
Any sensitive values from settings data or terminal output