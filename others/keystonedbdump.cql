Data to insert into Cassandra, equivalent to present in keystonedbdump file


INSERT INTO user (id, default_project_id, domain_id, enabled, extra, name, password) VALUES ( '90f0471df5a749e59e997f772b146b07', NULL, 'default', True, '{"email": "demo@example.com"}', 'demo', '$6$rounds=40000$5Y2F4aQVM9I6N0xX$GcgsL3QoZG8MkPCngRyU6mykw.SeF3IqCmAU4TUA.QkzNiq9SihYQSDXVPY1TEFvcGhadL2JG1Dmz6OGxEIKA/');
INSERT INTO user (id, default_project_id, domain_id, enabled, extra, name, password) VALUES ( 'cf1f87101f8d4e8a92dc8a5a7cfa319e', NULL, 'default', True, '{"email": null}', 'admin', '$6$rounds=40000$mYA6Iwpl6dm.ijML$swgnT0JM/lLoagtwnY.JL/e24TRh97koMIO/Gx9tDHajzeZpuEXQKLcYJ0.DQoVxIpCCPV0xKME6llo73oqhz/');

INSERT INTO group (id, description, domain_id, extra, name) VALUES ( 'c330e009e6674b479544cab7feef17ef', 'openstack admin group', 'default', '{}', 'admins');
INSERT INTO group (id, description, domain_id, extra, name) VALUES ( 'd32b0f69face4b42a7c482b8cac447e6', 'non-admin group', 'default', '{}', 'nonadmins');

INSERT INTO domain_id_user_name_to_user_id (domain_id, name, user_id) VALUES ( 'default', 'demo', '90f0471df5a749e59e997f772b146b07');
INSERT INTO domain_id_user_name_to_user_id (domain_id, name, user_id) VALUES ( 'default', 'admin', 'cf1f87101f8d4e8a92dc8a5a7cfa319e');

INSERT INTO domain_id_group_name_to_group_id (domain_id, name, group_id) VALUES ( 'default', 'admins', 'c330e009e6674b479544cab7feef17ef');
INSERT INTO domain_id_group_name_to_group_id (domain_id, name, group_id) VALUES ( 'default', 'nonadmins', 'd32b0f69face4b42a7c482b8cac447e6');

INSERT INTO role_assignment (type, actor_id, target_id, role_id, inherited) VALUES ( 'UserProject', '90f0471df5a749e59e997f772b146b07', '03a5bd375fbc415a9be7f280e6191b29', 'a4f4de83ad05477d98a271ec79e44ad2', False);
INSERT INTO role_assignment (type, actor_id, target_id, role_id, inherited) VALUES ( 'UserProject', '90f0471df5a749e59e997f772b146b07', '2438933b3e0f4420b099209d55ced8bc', 'a4f4de83ad05477d98a271ec79e44ad2', False);
INSERT INTO role_assignment (type, actor_id, target_id, role_id, inherited) VALUES ( 'UserProject', '90f0471df5a749e59e997f772b146b07', '2438933b3e0f4420b099209d55ced8bc', 'b76f278949b84582a89cd979223d936a', False);
INSERT INTO role_assignment (type, actor_id, target_id, role_id, inherited) VALUES ( 'UserProject', 'cf1f87101f8d4e8a92dc8a5a7cfa319e', '2438933b3e0f4420b099209d55ced8bc', '345e4b74170f4d889275880a9cfcccd2', False);
INSERT INTO role_assignment (type, actor_id, target_id, role_id, inherited) VALUES ( 'UserProject', 'cf1f87101f8d4e8a92dc8a5a7cfa319e', '5488164611064755a49ff7b9d456bc49', '345e4b74170f4d889275880a9cfcccd2', False);



INSERT INTO project (id, description, domain_id, enabled, extra, parent_id, name) VALUES ('03a5bd375fbc415a9be7f280e6191b29', '', 'default', True, '{}', '', 'invisible_to_admin');
INSERT INTO project (id, description, domain_id, enabled, extra, parent_id, name) VALUES ('2438933b3e0f4420b099209d55ced8bc', '', 'default', True, '{}', '', 'demo');
INSERT INTO project (id, description, domain_id, enabled, extra, parent_id, name) VALUES ('5488164611064755a49ff7b9d456bc49', '', 'default', True, '{}', '', 'admin');
INSERT INTO project (id, description, domain_id, enabled, extra, parent_id, name) VALUES ('fc1e56d8c6b746ba9e0ef2810e84acbd', '', 'default', True, '{}', '', 'service');

INSERT INTO project_gsi_name_domain_id (name, domain_id, project_id) VALUES ('invisible_to_admin', 'default', '03a5bd375fbc415a9be7f280e6191b29');
INSERT INTO project_gsi_name_domain_id (name, domain_id, project_id) VALUES ('demo', 'default', '2438933b3e0f4420b099209d55ced8bc');
INSERT INTO project_gsi_name_domain_id (name, domain_id, project_id) VALUES ('admin', 'default', '5488164611064755a49ff7b9d456bc49');
INSERT INTO project_gsi_name_domain_id (name, domain_id, project_id) VALUES ('service', 'default', 'fc1e56d8c6b746ba9e0ef2810e84acbd');


INSERT INTO domain (id, name, enabled, extra) VALUES ('default', 'Default', True, '{"description": "Owns users and tenants (i.e. projects) available on Identity API v2."}');

INSERT INTO domain_gsi_name (name, domain_id) VALUES ('Default', 'default');



INSERT INTO service (id, type, enabled, extra) VALUES ('58138146b86b4627bd6500856826a5d8', 'identity', True, '{"name": "keystone", "description": "Keystone Identity Service"}');


INSERT INTO endpoint (id, legacy_endpoint_id, interface, service_id, url, extra, enabled, region_id) VALUES ('01092d12a8064c7caccba2b5b9e5f24f', '59fdfb5a5c884451afe2e520f8020785', 'public', '58138146b86b4627bd6500856826a5d8', 'http://10.0.2.15:5000/v2.0', '{}', True, 'RegionOne');
INSERT INTO endpoint (id, legacy_endpoint_id, interface, service_id, url, extra, enabled, region_id) VALUES ('7b5fa9a506824b8a8970720ab126e198', '59fdfb5a5c884451afe2e520f8020785', 'admin', '58138146b86b4627bd6500856826a5d8', 'http://10.0.2.15:35357/v2.0', '{}', True, 'RegionOne');
INSERT INTO endpoint (id, legacy_endpoint_id, interface, service_id, url, extra, enabled, region_id) VALUES ('c4b8ecbc073e47e6b194552754e1e575', '59fdfb5a5c884451afe2e520f8020785', 'internal', '58138146b86b4627bd6500856826a5d8', 'http://10.0.2.15:5000/v2.0', '{}', True, 'RegionOne');


INSERT INTO region (id, description, parent_region_id, extra) VALUES ('RegionOne', '', '', '{}');
