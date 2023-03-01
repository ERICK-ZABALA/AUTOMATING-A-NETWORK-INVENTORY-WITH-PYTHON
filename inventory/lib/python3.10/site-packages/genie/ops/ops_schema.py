from genie.metaparser.util.schemaengine import Any

class Ops_structure:

    ops_schema = {
        'acl': {
            'info': {
                'acls': {
                    Any(): {
                        'name': Any(),
                        'type': Any(),
                        'aces': {
                            Any(): {
                                'name': Any(),
                                'matches': {
                                    'l2': {
                                        'eth': {
                                            'destination_mac_address': Any(),
                                            'source_mac_address': Any(),
                                            'ether_type': Any(),
                                        },
                                    },
                                    'l3': {
                                        'ipv4': {
                                            'dscp': Any(),
                                            'ecn': Any(),
                                            'length': Any(),
                                            'ttl': Any(),
                                            'ttl_operator': Any(),
                                            'protocol': Any(),
                                            'ihl': Any(),
                                            'flags': Any(),
                                            'offset': Any(),
                                            'precedence': Any(),
                                            'identification': Any(),
                                            'destination_ipv4_network': {
                                                Any(): {
                                                    'destination_ipv4_network': Any(),
                                                },
                                            },
                                            'source_ipv4_network': {
                                                Any(): {
                                                    'source_ipv4_network': Any(),
                                                },
                                            },
                                        },
                                        'ipv6': {
                                            'dscp': Any(),
                                            'ecn': Any(),
                                            'length': Any(),
                                            'ttl': Any(),
                                            'ttl_operator': Any(),
                                            'protocol': Any(),
                                            'destination_ipv6_network': {
                                                Any(): {
                                                    'destination_ipv6_network': Any(),
                                                },
                                            },
                                            'source_ipv6_network': {
                                                Any(): {
                                                    'source_ipv6_network': Any(),
                                                },
                                            },
                                            'flow_label': Any(),
                                        },
                                    },
                                    'l4': {
                                        'tcp': {
                                            'sequence_number': Any(),
                                            'acknowledgement_number': Any(),
                                            'data_offset': Any(),
                                            'reserved': Any(),
                                            'flags': Any(),
                                            'window_size': Any(),
                                            'urgent_pointer': Any(),
                                            'options': Any(),
                                            'established': Any(),
                                            'source-port': {
                                                'range': {
                                                    'lower_port': Any(),
                                                    'upper_port': Any(),
                                                },
                                                'operator': {
                                                    'operator': Any(),
                                                    'port': Any(),
                                                },
                                            },
                                            'destination_port': {
                                                'range': {
                                                    'lower_port': Any(),
                                                    'upper_port': Any(),
                                                },
                                                'operator': {
                                                    'operator': Any(),
                                                    'port': Any(),
                                                },
                                            },
                                        },
                                        'udp': {
                                            'length': Any(),
                                            'source-port': {
                                                'range': {
                                                    'lower_port': Any(),
                                                    'upper_port': Any(),
                                                },
                                                'operator': {
                                                    'operator': Any(),
                                                    'port': Any(),
                                                },
                                            },
                                            'destination_port': {
                                                'range': {
                                                    'lower_port': Any(),
                                                    'upper_port': Any(),
                                                },
                                                'operator': {
                                                    'operator': Any(),
                                                    'port': Any(),
                                                },
                                            },
                                        },
                                        'icmp': {
                                            'type': Any(),
                                            'code': Any(),
                                            'rest_of_header': Any(),
                                        },
                                    },
                                    'egress_interface': Any(),
                                    'ingress_interface': Any(),
                                },
                                'actions': {
                                    'forwarding': Any(),
                                    'logging': Any(),
                                },
                                'statistics': {
                                    'matched_packets': Any(),
                                    'matched_octets': Any(),
                                },
                            },
                        },
                    },
                },
                'attachment_points': {
                    Any(): {
                        'interface_id': Any(),
                        'ingress': {
                            'acl_sets': {
                                Any(): {
                                    'name': Any(),
                                    'ace_statistics': {
                                        'matched_packets': Any(),
                                        'matched_octets': Any(),
                                    },
                                },
                            },
                        },
                        'egress': {
                            'acl_sets': {
                                Any(): {
                                    'name': Any(),
                                    'ace_statistics': {
                                        'matched_packets': Any(),
                                        'matched_octets': Any(),
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'arp': {
            'info': {
                'max_entries': Any(),
                'global_static_table': {
                    Any(): {
                        'ip_address': Any(),
                        'mac_address': Any(),
                        'encap_type': Any(),
                        'interface': Any(),
                        'alias': Any(),
                    },
                },
                'statistics': {
                    'in_requests_pkts': Any(),
                    'in_replies_pkts': Any(),
                    'in_gratuitous_pkts': Any(),
                    'out_requests_pkts': Any(),
                    'out_replies_pkts': Any(),
                    'out_gratuitous_pkts': Any(),
                    'in_drops': Any(),
                    'out_drops': Any(),
                    'in_total': Any(),
                    'out_total': Any(),
                    'all_dynamic_pkts': Any(),
                    'all_static_pkts': Any(),
                    'entries_total': Any(),
                    'incomplete_total': Any(),
                },
                'interfaces': {
                    Any(): {
                        'arp_dynamic_learning': {
                            'expire_time': Any(),
                            'proxy_enable': Any(),
                            'local_proxy_enable': Any(),
                            'statistics': {
                                'in_request_pkts': Any(),
                                'in_replies_pkts': Any(),
                                'in_gratuitous_pkts': Any(),
                                'out_requests_pkts': Any(),
                                'out_replies_pkts': Any(),
                                'out_gratuitous_pkts': Any(),
                            },
                        },
                        'ipv4': {
                            'neighbors': {
                                Any(): {
                                    'ip': Any(),
                                    'link_layer_address': Any(),
                                    'origin': Any(),
                                    'remaining_expire_time': Any(),
                                },
                            },
                        },
                    },
                },
            },
        },

        'bgp': {
            'info': {
                'instance': {
                    Any(): {
                        'bgp_id': Any(),
                        'protocol_state': Any(),
                        'peer_session': {
                            Any(): {
                                'fall_over_bfd': Any(),
                                'suppress_four_byte_as_capability': Any(),
                                'description': Any(),
                                'disable_connected_check': Any(),
                                'ebgp_multihop_enable': Any(),
                                'ebgp_multihop_max_hop': Any(),
                                'local_as_as_no': Any(),
                                'local_no_prepend': Any(),
                                'local_dual_as': Any(),
                                'local_replace_as': Any(),
                                'password_text': Any(),
                                'remote_as': Any(),
                                'shutdown': Any(),
                                'keepalive_interval': Any(),
                                'holdtime': Any(),
                                'transport_connection_mode': Any(),
                                'update_source': Any(),
                            },
                        },
                        'peer_policy': {
                            Any(): {
                                'allowas_in': Any(),
                                'allowas_in_as_number': Any(),
                                'as_override': Any(),
                                'default_originate': Any(),
                                'default_originate_route_map': Any(),
                                'route_map_name_in': Any(),
                                'route_map_name_out': Any(),
                                'maximum_prefix_max_prefix_no': Any(),
                                'maximum_prefix_threshold': Any(),
                                'maximum_prefix_restart': Any(),
                                'maximum_prefix_warning_only': Any(),
                                'next_hop_self': Any(),
                                'route_reflector_client': Any(),
                                'send_community': Any(),
                                'soft_reconfiguration': Any(),
                                'soo': Any(),
                            },
                        },
                        'vrf': {
                            Any(): {
                                'always_compare_med': Any(),
                                'bestpath_compare_routerid': Any(),
                                'bestpath_cost_community_ignore': Any(),
                                'bestpath_med_missin_at_worst': Any(),
                                'cluster_id': Any(),
                                'confederation_identifier': Any(),
                                'confederation_peer_as': Any(),    
                                'graceful_restart': Any(),
                                'graceful_restart_restart_time': Any(),
                                'graceful_restart_stalepath_time': Any(),
                                'log_neighbor_changes': Any(),
                                'router_id': Any(),
                                'keepalive_interval': Any(),
                                'holdtime': Any(),
                                'enforce_first_as': Any(),
                                'fast_external_fallover': Any(),
                                'default_choice_ipv4_unicast': Any(),
                                'address_family': {
                                    Any(): {
                                        'dampening': Any(),
                                        'dampening_route_map': Any(),
                                        'dampening_half_life_time': Any(),
                                        'dampening_reuse_time': Any(),
                                        'dampening_suppress_time': Any(),
                                        'dampening_max_suppress_time': Any(),
                                        'nexthop_route_map': Any(),
                                        'nexthop_trigger_enable': Any(),
                                        'nexthop_trigger_delay_critical': Any(),
                                        'nexthop_trigger_delay_non_critical': Any(),
                                        'client_to_client_reflection': Any(),
                                        'distance_extern_as': Any(),
                                        'distance_internal_as': Any(),
                                        'distance_local': Any(),
                                        'maximum_paths_ebgp': Any(),
                                        'maximum_paths_ibgp': Any(),
                                        'maximum_paths_eibgp': Any(),
                                        'aggregate_address_ipv4_address': Any(),
                                        'aggregate_address_ipv4_mask': Any(),
                                        'aggregate_address_as_set': Any(),
                                        'aggregate_address_summary_only': Any(),
                                        'network_number': Any(),
                                        'network_mask': Any(),
                                        'network_route_map': Any(),
                                        'redist_isis': Any(),
                                        'redist_isis_metric': Any(),
                                        'redist_isis_route_policy': Any(),
                                        'redist_ospf': Any(),
                                        'redist_ospf_metric': Any(),
                                        'redist_ospf_route_policy': Any(),
                                        'redist_rip': Any(),
                                        'redist_rip_metric': Any(),
                                        'redist_rip_route_policy': Any(),
                                        'redist_static': Any(),
                                        'redist_static_metric': Any(),
                                        'redist_static_route_policy': Any(),
                                        'redist_connected': Any(),
                                        'redist_connected_metric': Any(),
                                        'redist_connected_route_policy': Any(),
                                        'v6_aggregate_address_ipv6_address': Any(),
                                        'v6_aggregate_address_as_set': Any(),
                                        'v6_aggregate_address_summary_only': Any(),
                                        'v6_network_number': Any(),
                                        'v6_network_route_map': Any(),
                                        'v6_allocate_label_all': Any(),
                                        'retain_rt_all': Any(),
                                        'label_allocation_mode': Any(),
                                    },
                                },
                                'neighbor': {
                                    Any(): {
                                        'fall_over_bfd': Any(),
                                        'suppress_four_byte_as_capability': Any(),
                                        'description': Any(),
                                        'disable_connected_check': Any(),
                                        'ebgp_multihop': Any(),
                                        'ebgp_multihop_max_hop': Any(),
                                        'inherit_peer_session': Any(),
                                        'local_as_as_no': Any(),
                                        'local_as_no_prepend': Any(),
                                        'local_as_replace_as': Any(),
                                        'local_as_dual_as': Any(),
                                        'remote_as': Any(),
                                        'remove_private_as': Any(),
                                        'shutdown': Any(),
                                        'keepalive_interval': Any(),
                                        'holdtime': Any(),
                                        'bgp_version': Any(),
                                        'installed_prefixes': Any(),
                                        'session_state': Any(),
                                        'bgp_negotiated_keepalive_timers': {
                                            'keepalive_interval': Any(),
                                            'hold_time': Any(),
                                        },
                                        'bgp_session_transport': {
                                            'connection': {
                                                'state': Any(),
                                                'mode': Any(),
                                                'last_reset': Any(),
                                                'reset_reason': Any(),
                                            },
                                            'transport': {
                                                'local_port': Any(),
                                                'local_host': Any(),
                                                'foreign_port': Any(),
                                                'foreign_host': Any(),
                                                'mss': Any(),
                                            },
                                        },
                                        'minimum_neighbor_hold': Any(),
                                        'up_time': Any(),
                                        'update_source': Any(),
                                        'password_text': Any(),
                                        'bgp_negotiated_capabilities': {
                                            'route_refresh': Any(),
                                            'four_octets_asn': Any(),
                                            'vpnv4_unicast': Any(),
                                            'vpnv6_unicast': Any(),
                                            'ipv4_mvpn': Any(),
                                            'graceful_restart': Any(),
                                            'enhanced_refresh': Any(),
                                            'multisession': Any(),
                                            'stateful_switchover': Any(),
                                        },
                                        'bgp_neighbor_counters': {
                                            'messages': {
                                                'sent': {
                                                    'opens': Any(),
                                                    'updates': Any(),
                                                    'notifications': Any(),
                                                    'keepalives': Any(),
                                                    'route_refreshes': Any(),
                                                },
                                                'received': {
                                                    'opens': Any(),
                                                    'updates': Any(),
                                                    'notifications': Any(),
                                                    'keepalives': Any(),
                                                    'route_refreshes': Any(),
                                                },
                                            },
                                        },
                                        'address_family': {
                                            Any(): {
                                                'session_state': Any(),
                                                'bgp_table_version': Any(),
                                                'routing_table_version': Any(),
                                                'prefixes': {
                                                    'total_entries': Any(),
                                                    'memory_usage': Any(),
                                                },
                                                'path': {
                                                    'total_entries': Any(),
                                                    'memory_usage': Any(),
                                                },
                                                'total_memory': Any(),
                                                'allowas_in': Any(),
                                                'allowas_in_as_number': Any(),
                                                'inherit_peer_policy': {
                                    Any(): {
                                    'inherit_peer_seq': Any(),
                                                    },
                                                },
                                                'maximum_prefix_max_prefix_no': Any(),
                                                'maximum_prefix_threshold': Any(),
                                                'maximum_prefix_restart': Any(),
                                                'maximum_prefix_warning_only': Any(),
                                                'route_map_name_in': Any(),
                                                'route_map_name_out': Any(),
                                                'route_reflector_client': Any(),
                                                'send_community': Any(),
                                                'soft_configuration': Any(),
                                                'next_hop_self': Any(),
                                                'as_override': Any(),
                                                'default_originate': Any(),
                                                'default_originate_route_map': Any(),
                                                'soo': Any(),
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            'routes_per_peer': {
                'instance': {
                    Any(): {
                        'vrf': {
                            Any(): {
                                'neighbor': {
                                    Any(): {
                                        'remote_as': Any(),
                                        'address_family': {
                                            Any(): {
                                                'route_distinguisher': Any(),
                                                'default_vrf': Any(),
                                                'msg_rcvd': Any(),
                                                'msg_sent': Any(),
                                                'tbl_ver': Any(),
                                                'input_queue': Any(),
                                                'output_queue': Any(),
                                                'up_down': Any(),
                                                'state_pfxrcd': Any(),
                                                'advertised': {
                                                    Any(): {
                                                        'index': {
                                                            Any(): {
                                                                'next_hop': Any(),
                                                                'status_codes': Any(),
                                                                'origin_codes': Any(),
                                                                'metric': Any(),
                                                                'locprf': Any(),
                                                                'weight': Any(),
                                                                'path': Any(),
                                                            },
                                                        },
                                                    },
                                                },
                                                'routes': {
                                                    Any(): {
                                                        'index': {
                                                            Any(): {
                                                                'next_hop': Any(),
                                                                'status_codes': Any(),
                                                                'origin_codes': Any(),
                                                                'metric': Any(),
                                                                'locprf': Any(),
                                                                'weight': Any(),
                                                                'path': Any(),
                                                            },
                                                        },
                                                    },
                                                },
                                                'received_routes': {
                                                    Any(): {
                                                        'index': {
                                                            Any(): {
                                                                'next_hop': Any(),
                                                                'status_codes': Any(),
                                                                'origin_codes': Any(),
                                                                'metric': Any(),
                                                                'locprf': Any(),
                                                                'weight': Any(),
                                                                'path': Any(),
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            'table': {
                'instance': {
                    Any(): {
                        'vrf': {
                            Any(): {
                                'address_family': {
                                    Any(): {
                                        'route_distinguisher': Any(),
                                        'default_vrf': Any(),
                                        'route_identifier': Any(),
                                        'local_as': Any(),
                                        'bgp_table_version': Any(),
                                        'routing_table_version': Any(),
                                        'paths': Any(),
                                        'prefixes': {
                                            Any(): {
                                                'table_version': Any(),
                                                'index': {
                                                    Any(): {
                                                        'next_hop': Any(),
                                                        'next_hop_igp_metric': Any(),
                                                        'gateway': Any(),
                                                        'cluster_id': Any(),
                                                        'update_group': Any(),
                                                        'status_codes': Any(),
                                                        'origin_codes': Any(),
                                                        'metric': Any(),
                                                        'localpref': Any(),
                                                        'weight': Any(),
                                                        'ext_community': Any(),
                                                        'mpls_labels_inout': Any(),
                                                        'originator': Any(),
                                                        'cluster_list': Any(),
                                                        'path': Any(),
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'dot1x': {
            'info': {
                'version': Any(),
                'credentials': {
                    Any(): {
                        'profile_name': Any(),
                        'username': Any(),
                        'password': {
                            'type': Any(),
                            'secret': Any(),
                        },
                        'pki_trustpoint': Any(),
                    },
                },
                'critical': {
                    'eapol': Any(),
                    'recovery': {
                        'relay': Any(),
                    },
                },
                'test': {
                    'timeout': Any(),
                },
                'supplicant': {
                    'force_multicast': Any(),
                },
                'system_auth_control': Any(),
                'sessions': {
                    'authorized_clients': Any(),
                    'unauthorized_clients': Any(),
                    'total': Any(),
                },
                'interfaces': {
                    Any(): {
                        'interface': Any(),
                        'authenticator': {
                            'eap': {
                                'profile': Any(),
                            },
                        },
                        'credentials': Any(),
                        'max_reauth_req': Any(),
                        'max_req': Any(),
                        'max_start': Any(),
                        'pae': Any(),
                        'supplicant': {
                            'eap': {
                                'profile': Any(),
                            },
                        },
                        'timeout': {
                            'auth_period': Any(),
                            'held_period': Any(),
                            'quiet_period': Any(),
                            'ratelimit_period': Any(),
                            'server_timeout': Any(),
                            'start_period': Any(),
                            'supp_timeout': Any(),
                            'tx_period': Any(),
                        },
                        'statistics': {
                            'rxreq': Any(),
                            'rxinvalid': Any(),
                            'rxlenerr': Any(),
                            'rxtotal': Any(),
                            'txstart': Any(),
                            'txlogoff': Any(),
                            'txresp': Any(),
                            'txtotal': Any(),
                            'rxversion': Any(),
                            'lastrxsrcmac': Any(),
                        },
                        'clients': {
                            Any(): {
                                'client': Any(),
                                'status': Any(),
                                'eap_method': Any(),
                                'pae': Any(),
                                'session': {
                                    Any(): {
                                        'session_id': Any(),
                                        'auth_sm_state': Any(),
                                        'auth_bend_sm_state': Any(),
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'eigrp': {
            'info': {
                'eigrp_instance': {
                    Any(): {
                        'vrf': {
                            Any(): {
                                'address_family': {
                                    Any(): {
                                        'router_id': Any(),
                                        'named_mode': Any(),
                                        'name': Any(),
                                        'eigrp_interface': {
                                            Any(): {
                                                'passive': Any(),
                                                'hello_interval': Any(),
                                                'hold_timer': Any(),
                                                'auth_val': {
                                                    'auth_mode': Any(),
                                                    'auth_key': {
                                                        'key_chain': Any(),
                                                        'sha256_password': Any(),
                                                    },
                                                },
                                                'eigrp_nbr': {
                                                    Any(): {
                                                        'nbr_sw_ver': {
                                                            'os_majorver': Any(),
                                                            'os_minorver': Any(),
                                                            'tlv_majorrev': Any(),
                                                            'tlv_minorrev': Any(),
                                                        },
                                                        'nbr_stubinfo': {
                                                            'stubbed': Any(),
                                                            'receive_only': Any(),
                                                            'allow_connected': Any(),
                                                            'allow_static': Any(),
                                                            'allow_summary': Any(),
                                                            'static_nbr': Any(),
                                                            'allow_redist': Any(),
                                                            'allow_leaking': Any(),
                                                        },
                                                        'retransmit_count': Any(),
                                                        'retry_count': Any(),
                                                        'last_seq_number': Any(),
                                                        'srtt': Any(),
                                                        'rto': Any(),
                                                        'q_cnt': Any(),
                                                        'hold': Any(),
                                                        'uptime': Any(),
                                                        'peer_handle': Any(),
                                                        'prefixes': Any(),
                                                        'topology_ids_from_peer': Any(),
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'fdb': {
            'info': {
                'mac_learning': Any(),
                'mac_aging_time': Any(),
                'maximum_entries': Any(),
                'mac_table': {
                    'vlans': {
                        Any(): {
                            'vlan': Any(),
                            'mac_learning': Any(),
                            'mac_aging_time': Any(),
                            'mac_addresses': {
                                Any(): {
                                    'mac_address': Any(),
                                    'drop': {
                                        'drop': Any(),
                                        'age': Any(),
                                        'entry_type': Any(),
                                    },
                                    'interfaces': {
                                        Any(): {
                                            'interface': Any(),
                                            'age': Any(),
                                            'entry_type': Any(),
                                        },
                                    },
                                },
                            },
                        },
                    },
                    'total_mac_addresses': Any(),
                },
            },
        },

        'hsrp': {
            'info': {
                'enabled': Any(),
                Any(): {
                    'address_family': {
                        Any(): {
                            'version': {
                                Any(): {
                                    'groups': {
                                        Any(): {
                                            'bfd': {
                                                'address': Any(),
                                                'interface_name': Any(),
                                            },
                                            'tracked_interfaces': {
                                                Any(): {
                                                    'interface_name': Any(),
                                                    'priority_decrement': Any(),
                                                },
                                            },
                                            'tracked_objects': {
                                                Any(): {
                                                    'object_name': Any(),
                                                    'priority_decrement': Any(),
                                                },
                                            },
                                            'timers': {
                                                'hello_msec_flag': Any(),
                                                'hello_msec': Any(),
                                                'hello_sec': Any(),
                                                'hold_msec_flag': Any(),
                                                'hold_msec': Any(),
                                                'hold_sec': Any(),
                                            },
                                            'primary_ipv4_address': {
                                                'virtual_ip_learn': Any(),
                                                'address': Any(),
                                            },
                                            'secondary_ipv4_addresses': {
                                                Any(): { 
                                                    'address': Any(),
                                                },
                                            },
                                            'authentication': Any(),
                                            'link_local_ipv6_address': {
                                                'address': Any(),
                                                'auto_configure': Any(),
                                            },
                                            'global_ipv6_addresses': {
                                                Any(): {
                                                    'address': Any(),
                                                },
                                            },
                                            'priority': Any(),
                                            'preempt': Any(),
                                            'session_name': Any(),
                                            'virtual_mac_address': Any(),
                                            'group_number': Any(),
                                            'statistics': {
                                                'active_transitions': Any(),
                                                'standby_transitions': Any(),
                                                'speak_transitions': Any(),
                                                'listen_transitions': Any(),
                                                'learn_transitions': Any(),
                                                'init_transitions': Any(),
                                                'hello_packets_sent': Any(),
                                                'resign_packets_sent': Any(),
                                                'coup_packets_sent': Any(),
                                                'hello_packets_received': Any(),
                                                'resign_packets_received': Any(),
                                                'coup_packets_received': Any(),
                                                'auth_fail_received': Any(),
                                                'invalid_timer_received': Any(),
                                                'mismatch_virtual_ip_address_received': Any(),
                                            },
                                            'active_ip_address': Any(),
                                            'active_ipv6_address': Any(),
                                            'active_mac_address': Any(),
                                            'active_router': Any(),
                                            'standby_ip_address': Any(),
                                            'standby_ipv6_address': Any(),
                                            'standby_mac_address': Any(),
                                            'standby_router': Any(),
                                            'hsrp_router_state': Any(),
                                        },
                                    },
                                    'slave_groups': {
                                        Any(): {
                                            'secondary_ipv4_addresses': {
                                                Any(): {
                                                    'address': Any(),
                                                },
                                            },
                                            'primary_ipv4_address': Any(),
                                            'link_local_ipv6_address': {
                                                'address': Any(),
                                                'auto_configure': Any(),
                                            },
                                            'global_ipv6_addresses': {
                                                Any(): {
                                                    'address': Any(),
                                                },
                                            },
                                            'follow': Any(),
                                            'virtual_mac_address': Any(),
                                            'slave_group_number': Any(),
                                        },
                                    },
                                },
                            },
                        },
                    },
                    'bfd': {
                        'enabled': Any(),
                        'detection_multiplier': Any(),
                        'interval': Any(),
                    },
                    'delay': {
                        'minimum_delay': Any(),
                        'reload_delay': Any(),
                    },
                    'mac_refresh': Any(),
                    'use_bia': Any(),
                    'redirects_disable': Any(),
                    'interface': Any(),
                },
                'logging': {
                    'state_change_disable': Any(),
                },
            },
        },

        'igmp': {
            'info': {
                'vrfs': {
                    Any(): {
                        'max_groups': Any(),
                        'groups_count': Any(),
                        'ssm_map': {
                            Any(): { 
                                'source_addr': Any(),
                                'group_policy': Any(),
                                'group_range': Any(),
                                'group_address': Any(),
                            },
                        },
                        'interfaces': {
                            Any(): {
                                'enable': Any(),
                                'last_member_query_interval': Any(),
                                'group_policy': Any(),
                                'immediate_leave': Any(),
                                'max_groups': Any(),
                                'query_interval': Any(),
                                'query_max_response_time': Any(),
                                'robustness_variable': Any(),
                                'version': Any(),
                                'oper_status': Any(),
                                'querier': Any(),
                                'joined_group': Any(),
                                'join_group': {
                                    Any(): {
                                        'group': Any(),
                                        'source': Any(),
                                    },
                                },
                                'static_group': {
                                    Any(): {
                                        'group': Any(),
                                        'source': Any(),
                                    },
                                },
                                'group': {
                                    Any(): {
                                        'expire': Any(),
                                        'host_count': Any(),
                                        'up_time': Any(),
                                        'host': Any(),
                                        'last_reporter': Any(),
                                        'source': {
                                            Any(): {
                                                'expire': Any(),
                                                'up_time': Any(),
                                                'last_reporter': Any(),
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'interface': {
            'info': {
                Any(): {
                    'description': Any(),
                    'type': Any(),
                    'oper_status': Any(),
                    'last_change': Any(),
                    'phys_address': Any(),
                    'mtu': Any(),
                    'enabled': Any(),
                    'vlan_id': Any(),
                    'access_vlan': Any(),
                    'trunk_vlans': Any(),
                    'mac_address': Any(),
                    'auto_negotiate': Any(),
                    'duplex_mode': Any(),
                    'port_speed': Any(),
                    'switchport_enable': Any(),
                    'switchport_mode': Any(),
                    'medium': Any(),
                    'delay': Any(),
                    'port_channel': {
                        'port_channel_member': Any(),
                        'port_channel_int': Any(),
                        'port_channel_member_intfs': Any(),
                    },
                    'flow_control': {
                        'receive': Any(),
                        'send': Any(),
                    },
                    'bandwidth': Any(),
                    'link_status': Any(),
                    'vrf': Any(),
                    'vrf_downstream': Any(),
                    'accounting': {
                        Any(): {
                            'pkts_in': Any(),
                            'pkts_out': Any(),
                            'chars_in': Any(),
                            'chars_out': Any(),
                        },
                    },
                    'counters': {
                        'rate': {
                            'load_interval': Any(),
                            'in_rate': Any(),
                            'in_rate_pkts': Any(),
                            'out_rate': Any(),
                            'out_rate_pkts': Any(),
                        },
                        'in_pkts': Any(),
                        'in_octets': Any(),
                        'in_unicast_pkts': Any(),
                        'in_broadcast_pkts': Any(),
                        'in_multicast_pkts': Any(),
                        'in_discards': Any(),
                        'in_errors': Any(),
                        'in_unknown_protos': Any(),
                        'in_mac_control_frames': Any(),
                        'in_mac_pause_frames': Any(),
                        'in_oversize_frames': Any(),
                        'in_jabber_frames': Any(),
                        'in_fragment_frames': Any(),
                        'in_8021q_frames': Any(),
                        'in_crc_errors': Any(),
                        'out_pkts': Any(),
                        'out_octets': Any(),
                        'out_unicast_pkts': Any(),
                        'out_broadcast_pkts': Any(),
                        'out_multicast_pkts': Any(),
                        'out_discard': Any(),
                        'out_errors': Any(),
                        'out_mac_control_frames': Any(),
                        'out_mac_pause_frames': Any(),
                        'out_8021q_frames': Any(),
                        'last_clear': Any(),
                    },
                    'encapsulation': {
                        'enacapsulation': Any(),
                        'first_dot1q': Any(),
                        'second_dot1q': Any(),
                        'native_vlan': Any(),
                    },
                    'ipv4': {
                        Any(): {
                            'ip': Any(),
                            'prefix_length': Any(),
                            'origin': Any(),
                            'sedondary': Any(),
                            'route_tag': Any(),
                            'secondary_vrf': Any(),
                        },
                        'unnumbered': {
                            'interface_ref': Any(),
                        },
                    },
                    'ipv6': {
                        Any(): {
                            'ip': Any(),
                            'prefix_length': Any(),
                            'anycast': Any(),
                            'eui_64': Any(),
                            'route_tag': Any(),
                            'origin': Any(),
                            'status': Any(),
                            'autoconf': {
                                'valid_lifetime': Any(),
                                'preferred_lifetime': Any(),
                            },
                        },
                        'unnumbered': {
                            'interface_ref': Any(),
                        },
                        'enabled': Any(),
                    },
                },
            },
            
            
        },

        'isis': {
            'info': {
                'instance': {
                    Any(): {
                        'process_id': Any(),
                        'vrf': {
                            Any(): {
                                'vrf': Any(),
                                'enable': Any(),
                                'system_id': Any(),
                                'area_address': Any(),
                                'nsel': Any(),
                                'maximum_area_addresses': Any(),
                                'mpls': {
                                    'ipv4_router_id': Any(),
                                    'ipv6_router_id': Any(),
                                    'ldp':{
                                        'igp-sync': Any(),
                                    },
                                },
                                'lsp_mtu': Any(),
                                'lsp_lifetime': Any(),
                                'lsp_refresh': Any(),
                                'graceful_restart': {
                                    'enable': Any(),
                                    'restart_interval': Any(),
                                },
                                'nsr': {
                                    'enable': Any(),
                                },
                                'authentication': {
                                    'authentication_type': {
                                        'key_chain': Any(),
                                        'password': {
                                            'key': Any(),
                                            'crypto_algorithm': Any(),
                                        },
                                    },
                                    'level_1': {
                                        'authentication_type': {
                                            'key_chain': Any(),
                                            'password': {
                                                'key': Any(),
                                                'crypto_algorithm': Any(),
                                            },
                                        },
                                    },
                                    'level_2': {
                                        'authentication_type': {
                                            'key_chain': Any(),
                                            'password': {
                                                'key': Any(),
                                                'crypto_algorithm': Any(),
                                            },
                                        },
                                    },
                                },
                                'metric_type': {
                                    'value': Any(),
                                    'level_1': {
                                        'value': Any(),
                                    },
                                    'level_2': {
                                        'value': Any(),
                                    },
                                },
                                'default_metric': {
                                    'value': Any(),
                                    'level_1': {
                                        'value': Any(),
                                    },
                                    'level_2': {
                                        'value': Any(),
                                    },
                                },
                                'overload': {
                                    'status': Any(),
                                },
                                'fast_reroute': {
                                    'lfa': Any(),
                                    'protected_routes': {
                                        Any(): {
                                            'prefix': {
                                                Any(): {
                                                    'alternate': {
                                                        Any(): {
                                                            'alternate_type': Any(),
                                                            'best': Any(),
                                                            'non_best_reason': Any(),
                                                            'protection_available': Any(),
                                                            'alternate_metric1': Any(),
                                                            'alternate_metric2': Any(),
                                                            'alternate_metric3': Any(),
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                    'nonprotected_routes': {
                                        Any(): {
                                            'prefx': {
                                                Any(): {},
                                            },
                                        },
                                    },
                                    'protection_statistics': {
                                        'frr_protection_method': Any(),
                                        Any(): {
                                            'af': Any(),
                                            'total_routes': Any(),
                                            'unprotected_routes': Any(),
                                            'protected_routes': Any(),
                                            'linkprotected_routes': Any(),
                                            'nodeprotected_routes': Any(),
                                        },
                                    },
                                },
                                'spf_control': {
                                    'ietf_spf_delay': {
                                        'ietf_spf_delay_state': {
                                            'current_state': Any(),
                                            'remaining_time_to_learn': Any(),
                                            'remaining_hold_down': Any(),
                                            'last_event_received': Any(),
                                            'next_spf_time': Any(),
                                            'last_spf_time': Any(),
                                        },
                                    },
                                },
                                'spf_log': {
                                    Any(): {
                                        'id': Any(),
                                        'spf_type': Any(),
                                        'level': Any(),
                                        'schedule_timestamp': Any(),
                                        'start_timestamp': Any(),
                                        'end_timestamp': Any(),
                                        Any(): {
                                            'lsp': Any(),
                                            'sequence': Any(),
                                        },
                                    },
                                },
                                'lsp_log': {
                                    Any(): {
                                        'id': Any(),
                                        'level': Any(),
                                        'lsp': {
                                            'lsp': Any(),
                                            'sequence': Any(),
                                        },
                                        'received_timestamp': Any(),
                                        'change': Any(),
                                    },
                                },
                                'hostname_db': {
                                    'hostname': {
                                        Any(): {
                                            'hostname': Any(),
                                        },
                                    },
                                },
                                'topologies': {
                                    Any(): {
                                        'topology': Any(),
                                        'local_rib': {
                                            Any(): {
                                                'prefix': Any(),
                                                'next_hops': {
                                                    Any(): {
                                                        'outgoing_interface': Any(),
                                                        'next_hop': Any(),
                                                    },
                                                },
                                                'metric': Any(),
                                                'level': Any(),
                                                'route_tag': Any(),
                                            },
                                        },
                                        'preference': {
                                            'detail': {
                                                'internal': Any(),
                                                'external': Any(),
                                            },
                                            'coarse': {
                                                'default': Any(),
                                            },
                                        },
                                    },
                                },
                                'local_rib': {
                                    Any(): {
                                        'prefix': Any(),
                                        'next-hops': {
                                            Any(): {
                                                'outgoing_interface': Any(),
                                                'next_hop': Any(),
                                            },
                                        },
                                        'metric': Any(),
                                        'level': Any(),
                                        'route_tag': Any(),
                                    },
                                },
                                'system_counters': {
                                    Any(): {
                                        'level': Any(),
                                        'corrupted_lsps': Any(),
                                        'authentication_type_fails': Any(),
                                        'authentication_fails': Any(),
                                        'database_overload': Any(),
                                        'own_lsp_purge': Any(),
                                        'manual_address_drop_from_area': Any(),
                                        'max_sequence': Any(),
                                        'sequence_number_skipped': Any(),
                                        'id_len_mismatch': Any(),
                                        'partition_change': Any(),
                                        'lsp_errors': Any(),
                                        'spf_runs': Any(),
                                    },
                                },
                                'interfaces': {
                                    Any(): {
                                        'name': Any(),
                                        'level_type': Any(),
                                        'lsp_pacing_interval': Any(),
                                        'lsp_retransmit_interval': Any(),
                                        'passive': Any(),
                                        'hello_padding': {
                                            'enable': Any(),
                                        },
                                        'interface_type': Any(),
                                        'tag': Any(),
                                        'hello_authentication': {
                                            'authentication_type': {
                                                'key_chain': Any(),
                                                'password': {
                                                    'key': Any(),
                                                    'crypto_algorithm': Any(),
                                                },
                                            },
                                            'level_1': {
                                                'authentication_type': {
                                                    'key_chain': Any(),
                                                    'password': {
                                                        'key': Any(),
                                                        'crypto_algorithm': Any(),
                                                    },
                                                },
                                            },
                                            'level_2': {
                                                'authentication-type': {
                                                    'key_chain': Any(),
                                                    'password': {
                                                        'key': Any(),
                                                        'crypto_algorithm': Any(),
                                                    },
                                                },
                                            },
                                        },
                                        'hello_interval': {
                                            'interval': Any(),
                                            'level_1': {
                                                'interval': Any(),
                                            },
                                            'level_2': {
                                                'interval': Any(),
                                            },
                                        },
                                        'hello_multiplier': {
                                            'multiplier': Any(),
                                            'level_1': {
                                                'multiplier': Any(),
                                            },
                                            'level_2': {
                                                'multiplier': Any(),
                                            },
                                        },
                                        'priority': {
                                            'priority': Any(),
                                            'level_1': {
                                                'priority': Any(),
                                            },
                                            'level_2': {
                                                'priority': Any(),
                                            },
                                        },
                                        'adjacencies': {
                                            Any(): {
                                                'neighbor_snpa': {
                                                    Any(): {
                                                        'usage': {
                                                            Any(): {
                                                                'neighbor_systype': Any(),
                                                                'neighbor_extended_circuit_id': Any(),
                                                                'hold_timer': Any(),
                                                                'neighbor_priority': Any(),
                                                                'lastuptime': Any(),
                                                                'state': Any(),
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                        'event_counters': {
                                            'adjacency_changes': Any(),
                                            'adjacency_number': Any(),
                                            'init_fails': Any(),
                                            'adjacency_rejects': Any(),
                                            'id_len_mismatch': Any(),
                                            'max_area_addresses_mismatch': Any(),
                                            'authentication_type_fails': Any(),
                                            'authentication_fails': Any(),
                                            'lan_dis_changes': Any(),
                                        },
                                        'topologies': {
                                            Any(): {
                                                'name': Any(), 
                                                'metric': {
                                                    'metric': Any(),
                                                    'level_1': {
                                                        'metric': Any(),
                                                    },
                                                    'level_2': {
                                                        'metric': Any(),
                                                    },
                                                },
                                                'adjacencies': {
                                                    Any(): {
                                                        'neighbor_snpa': {
                                                            Any(): {
                                                                'level': {
                                                                    Any(): {
                                                                        'neighbor-systype': Any(),
                                                                        'neighbor-extended-circuit-id': Any(),
                                                                        'hold-timer': Any(),
                                                                        'neighbor_priority': Any(),
                                                                        'lastuptime': Any(),
                                                                        'state': Any(),
                                                                    },
                                                                },
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                        'packet_counters': {
                                            'level': {
                                                Any(): {
                                                    'level': Any(),
                                                    'iih': {
                                                        'in': Any(),
                                                        'out': Any(),
                                                    },
                                                    'ish': {
                                                        'in': Any(),
                                                        'out': Any(),
                                                    },
                                                    'esh': {
                                                        'in': Any(),
                                                        'out': Any(),
                                                    },
                                                    'lsp': {
                                                        'in': Any(),
                                                        'out': Any(),
                                                    },
                                                    'psnp': {
                                                        'in': Any(),
                                                        'out': Any(),
                                                    },
                                                    'csnp': {
                                                        'in': Any(),
                                                        'out': Any(),
                                                    },
                                                    'unknown': {
                                                        'in': Any(),
                                                        'out': Any(),
                                                    },
                                                },
                                            },
                                        },
                                        'address_family': {
                                            Any(): {
                                                'metric': {
                                                    'metric': Any(),
                                                    'level_1': {
                                                        'metric': Any(),
                                                    },
                                                    'level_2': {
                                                        'metric': Any(),
                                                    },
                                                },
                                                'bfd': {
                                                    'enable': Any(),
                                                },
                                                'mpls': {
                                                    'ldp':{
                                                        'igp_sync': Any(),
                                                    },
                                                },
                                                'fast_reroute': {
                                                    'lfa': {
                                                        'candidate_disabled': Any(),
                                                        'enable': Any(),
                                                        'level_1': {
                                                            'candidate_disable': Any(),
                                                            'enable': Any(),
                                                        },
                                                        'level_2': {
                                                            'candidate_disable': Any(),
                                                            'enable': Any(),
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            'lsdb': {
                'instance': {
                    Any(): {
                        'vrf': {
                            Any(): {
                                'level_db': {
                                    Any(): {
                                        Any(): {
                                            'decoded_completed': Any(),
                                            'raw_data': Any(),
                                            'lsp_id': Any(),
                                            'checksum': Any(),
                                            'remaining_lifetime': Any(),
                                            'sequence': Any(),
                                            'attributes': Any(),
                                            'ipv4_addresses': Any(),
                                            'ipv6_addresses': Any(),
                                            'ipv4_te_routerid': Any(),
                                            'ipv6_te_routerid': Any(),
                                            'protocol_supported': Any(),
                                            'dynamic_hostname': Any(),
                                            'authentication': {
                                                'authentication_type': Any(),
                                                'authentication_key': Any(),
                                            },
                                            'mt_entries': {
                                                Any(): {
                                                    'mt_id': Any(),
                                                    'attributes': Any(),
                                                },
                                            },
                                            'router_capabilities': {
                                                Any(): {
                                                    'flags': Any(),
                                                    'node_tags': {
                                                        Any(): {
                                                            'tag': Any(),
                                                        },
                                                    },
                                                    'binary': Any(),
                                                },
                                            },
                                            'is_neighbor': {
                                                Any(): {
                                                    'neighbor_id': Any(),
                                                    'i_e': Any(),
                                                    'default_metric': Any(),
                                                    'delay_metric': {
                                                        'metric': Any(),
                                                        'supported': Any(),
                                                    },
                                                    'expense_metric': {
                                                        'metric': Any(), 
                                                        'supported': Any(),
                                                    },
                                                    'error_metric': {
                                                        'metric': Any(),
                                                        'supported': Any(),
                                                    },
                                                },
                                            },
                                            'extended_is_neighbor': {
                                                Any(): {
                                                    'neighbor_id': Any(),
                                                    'metric': Any(),
                                                },
                                            },
                                            'ipv4_internal_reachability': {
                                                Any(): {
                                                    'up_down': Any(),
                                                    'i_e': Any(),
                                                    'ip_prefix': Any(),
                                                    'prefix_len': Any(),
                                                    'default_metric': Any(),
                                                    'delay_metric': {
                                                        'metric': Any(),
                                                        'supported': Any(),
                                                    },
                                                    'expense_metric': {
                                                        'metric': Any(),
                                                        'supported': Any(),
                                                    },
                                                    'error_metric': {
                                                        'metric': Any(),
                                                        'supported': Any(),
                                                    },
                                                },
                                            },
                                            'ipv4_external_reachability': {
                                                Any(): {
                                                    'up_down': Any(),
                                                    'i_e': Any(),
                                                    'ip_prefix': Any(),
                                                    'prefix_len': Any(),
                                                    'default_metric': Any(),
                                                    'delay_metric': {
                                                        'metric': Any(),
                                                        'supported': Any(),
                                                    },
                                                    'expense_metric': {
                                                        'metric': Any(),
                                                        'supported': Any(),
                                                    },
                                                    'error_metric': {
                                                        'metric': Any(),
                                                        'supported': Any(),
                                                    },
                                                },
                                            },
                                            'extended_ipv4_reachability': {
                                                Any(): {
                                                    'up_down': Any(),
                                                    'ip_prefix': Any(),
                                                    'prefix_len': Any(),
                                                    'metric': Any(),
                                                    'tag': Any(),
                                                    'tag64': Any(),
                                                    'external_prefix_flag': Any(),
                                                    'readvertisement_flag': Any(),
                                                    'node_flag': Any(),
                                                    'ipv4_source_router_id': Any(),
                                                    'ipv6_source_router_id': Any(),
                                                },
                                            },
                                            'mt_is_neighbor': {
                                                Any(): {
                                                    'mt_id': Any(),
                                                    'neighbor_id': Any(),
                                                    'metric': Any(),
                                                },
                                            },
                                            'mt_extended_ipv4_reachability': {
                                                Any(): {
                                                    'mt_id': Any(),
                                                    'up_down': Any(),
                                                    'ip_prefix': Any(),
                                                    'prefix_len': Any(),
                                                    'metric': Any(),
                                                    'tag': Any(),
                                                    'tag64': Any(),
                                                    'external_prefix_flag': Any(),
                                                    'readvertisement_flag': Any(),
                                                    'node_flag': Any(),
                                                    'ipv4_source_router_id': Any(),
                                                    'ipv6_source_router_id': Any(),
                                                },
                                            },
                                            'mt_ipv6_reachability': {
                                                Any(): {
                                                    'mt_id': Any(),
                                                    'up_down': Any(),
                                                    'ip_prefix': Any(),
                                                    'prefix_len': Any(),
                                                    'metric': Any(),
                                                    'tag': Any(),
                                                    'tag64': Any(),
                                                    'external_prefix_flag': Any(),
                                                    'readvertisement_flag': Any(),
                                                    'node_flag': Any(),
                                                    'ipv4_source_router_id': Any(),
                                                    'ipv6_source_router_id': Any(),
                                                },
                                            },
                                            'ipv6_reachability': {
                                                Any(): {
                                                    'up_down': Any(),
                                                    'ip_prefix': Any(),
                                                    'prefix_len': Any(),
                                                    'metric': Any(),
                                                    'tag': Any(),
                                                    'tag64': Any(),
                                                    'external_prefix_flag': Any(),
                                                    'readvertisement_flag': Any(),
                                                    'node_flag': Any(),
                                                    'ipv4_source_router_id': Any(),
                                                    'ipv6_source_router_id': Any(),
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'l2vpn': {
            'info': {
                'install_feature_set_mpls': Any(),
                'feature_set_mpls': Any(),
                'enable_mpls_l2vpn': Any(),
                'enable_evc': Any(),
                'instances': {
                    Any(): {
                        'type': {
                            Any(): {
                                'discovery_type': Any(),
                                'signaling_type': Any(),
                                'vpn_id': Any(),
                                'bgp_auto_discovery': {
                                    'route_distinguisher': Any(),
                                    Any(): {
                                        'route_target': Any(),
                                        'route_target_type': Any(),
                                    },
                                },
                                'bgp_signaling': {
                                    've_id': Any(),
                                    've_range': Any(),
                                },
                                'multicast': {
                                    Any(): {
                                        'type': Any(),
                                        'transport': {
                                            Any(): {
                                                'transport': Any(),
                                                'attribute_set': Any(),
                                            },
                                        },
                                        'signaling': {
                                            Any(): {
                                                'protocol': Any(),
                                            },
                                        },
                                    },
                                },
                                'name': {
                                    Any(): {
                                        'name': Any(),
                                        'system_bridge_domain': Any(),
                                        'attachment_circuit': {
                                            Any(): {
                                                'interface': Any(),
                                                'service_instance': Any(),
                                                'state': Any(),
                                            },
                                        },
                                        'bridge_domain': {
                                            Any(): {
                                                'bd_domain_id': Any(),
                                                'state': Any(),
                                                'ethernet_flow_point': {
                                                    Any(): {
                                                        'interface': Any(),
                                                        'instance': Any(),
                                                        'state': Any(),
                                                    },
                                                },
                                                'interface': {
                                                    Any(): {
                                                        'interface': Any(),
                                                        'state': Any(),
                                                    },
                                                },
                                                'pseudowire': {
                                                    Any(): {
                                                        'pw_id': {
                                                            Any(): {
                                                                'name': Any(),
                                                                'state': Any(),
                                                            },
                                                        },
                                                    },
                                                },
                                                'virtual_forwarding_instance': {
                                                    Any(): {
                                                        'name': Any(),
                                                    },
                                                },
                                            },
                                        },
                                        'pseudowire': {
                                            Any(): {
                                                'pw_id': {
                                                    Any(): {
                                                        'name': Any(),
                                                        'state': Any(),
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            'pw_info': {
                'pseudowires': {
                    Any(): {
                        'pw_id': {
                            Any(): {
                                'name': Any(),
                                'state': Any(),
                                'mtu': Any(),
                                'mac_withdraw': Any(),
                                'cw_negotiation': Any(),
                                'local_intf': Any(),
                                'local_circuit': Any(),
                                'configured_pw': {
                                    'peer_ip': Any(),
                                    'pw_id': Any(),
                                    'transmit_label': Any(),
                                    'receive_label': Any(),
                                },
                                'bgp_pw': {
                                    'remote_pe_id': Any(),
                                },
                                'bgp_ad_pw': {
                                    'remote_ve_id': Any(),
                                },
                                'signaling_protocol': {
                                    Any(): {
                                        'mpls_vc_labels': {
                                            'local': Any(),
                                            'remote': Any(),
                                        },
                                        'group_id': {
                                            'local': Any(),
                                            'remote': Any(),
                                        },
                                        'mtu': {
                                            'local': Any(),
                                            'remote': Any(),
                                        },
                                    },
                                },
                                'statistics': {
                                    'packets': {
                                        'received': Any(),
                                        'sent': Any(),
                                    },
                                    'bytes': {
                                        'received': Any(),
                                        'sent': Any(),
                                    },
                                },
                            },
                        },
                    },
                },
            },
            'bd_info': {
                'bridge_domain': {
                    Any(): {
                        'bd_domain_id': Any(),
                        'state': Any(),
                        'member_ports': Any(),
                        'mac_table': {
                            Any(): {
                                'pseudoport': Any(),
                                'mac_address': {
                                    Any(): {
                                        'mac_address': Any(),
                                        'aed': Any(),
                                        'policy': Any(),
                                        'tag': Any(),
                                        'age': Any(),
                                    },
                                },
                            },
                        },
                    },
                },
            },
            'vfi_info': {
                'vfi': {
                    Any(): {
                        'bd_vfi_name': Any(),
                        'bridge_group': Any(),
                        'state': Any(),
                        'type': Any(),
                        'signaling': Any(),
                        'vpn_id': Any(),
                        've_id': Any(),
                        've_range': Any(),
                        'rd': Any(),
                        'rt': Any(),
                        'bridge_domain': {
                            Any(): {
                                'attachment_circuits': {
                                    Any(): {
                                        'name': Any(),
                                    },
                                },
                                'vfi': {
                                    Any(): {
                                        'pw': {
                                            Any(): {
                                                'split_horizon': Any(),
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            'bgp_vpls_table': {
                'instance': {
                    Any(): {
                        'vrf': {
                            'default': {
                                'address_family': {
                                    'l2vpn vpls': {
                                        'table_version': Any(),
                                        'router_id': Any(),
                                        'rd': {
                                            Any(): {
                                                'rd': Any(),
                                                'rd_vrf': Any(),
                                                'prefix': {
                                                    Any(): {
                                                        'index': {
                                                            Any(): {
                                                                'next_hop': Any(),
                                                                'metric': Any(),
                                                                'localpref': Any(),
                                                                'weight': Any(),
                                                                'path': Any(),
                                                                'status_codes': Any(),
                                                                'origin_codes': Any(),
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'lag': {
            'info': {
                'enabled': Any(),
                'system_priority': Any(),
                'interfaces': {
                    Any(): {
                        'name': Any(),
                        'interval': Any(),
                        'lacp_mode': Any(),
                        'lacp_max_bundle': Any(),
                        'lacp_min_bundle': Any(),
                        'system_id_mac': Any(),
                        'system_priority': Any(),
                        'bundle_id': Any(),
                        'protocol': Any(),
                        'oper_status': Any(),
                        'members': {
                            Any(): {
                                'bundle_id': Any(),
                                'bundled' : Any(),
                                'interface': Any(),
                                'activity': Any(),
                                'non_silent': Any(),
                                'force': Any(),
                                'timeout': Any(),
                                'synchronization': Any(),
                                'aggregatable': Any(),
                                'collecting': Any(),
                                'distributing': Any(),
                                'system_id': Any(),
                                'oper_key': Any(),
                                'partner_id': Any(),
                                'partner_key': Any(),
                                'port_num': Any(),
                                'partner_port_num': Any(),
                                'lacp_port_priority': Any(),
                                'pagp_port_priority': Any(),
                                'age': Any(),
                                'counters': {
                                    'lacp_in_pkts': Any(),
                                    'lacp_out_pkts': Any(),
                                    'lacp_rx_errors': Any(),
                                    'lacp_tx_errors': Any(),
                                    'lacp_unknown_erros': Any(),
                                    'lacp_errors': Any(),
                                },
                            },
                        },
                    },
                },
            },
        },

        'lisp': {
            'info': {
                'lisp_router_instances': {
                    Any(): {
                        'lisp_router_instance_id': Any(),
                        'locator_sets': {
                            Any(): {
                                'locator_set_name': Any(),
                                'local_interface': {
                                    Any(): {
                                        'interface': Any(),
                                        'interface_type': Any(),
                                        'priority': Any(),
                                        'weight': Any(),
                                        'multicast_priority': Any(),
                                        'multicast_weight': Any(),
                                    },
                                },
                            },
                        },
                        'lisp_role': {
                            Any(): {
                                'lisp_role_type': Any(),
                            },
                        },
                        'lisp_router_id': {
                            'site_id': Any(),
                            'xtr_id': Any(),
                        },
                        'service': {
                            Any(): {
                                'service': Any(),
                                'lisp_role': {
                                    Any(): {
                                        'lisp_role_type': Any(),
                                    },
                                },
                                'virtual_network_ids': {
                                    Any(): {
                                        'lisp_role': {
                                            Any(): {
                                                'lisp_role_type': Any(),
                                            },
                                        },
                                    },
                                },
                                'map_server': {
                                    'enabled': Any(),
                                    'sites': {
                                        Any(): {
                                            'site_id': Any(),
                                            'auth_key': {
                                                'auth_key_value': Any(),
                                                'auth_key_type': Any(),
                                            },
                                        },
                                    },
                                    'virtual_network_ids': {
                                        Any(): {
                                            'vni': Any(),
                                            'extranets': {
                                                Any(): {
                                                    'extranet': Any(),
                                                    'home_instance_id': Any(),
                                                    'provider': {
                                                        Any(): {
                                                            'eid_record': Any(),
                                                            'bidirectional': Any(),
                                                        },
                                                    },
                                                    'subscriber': {
                                                        Any(): {
                                                            'eid_record': Any(),
                                                            'bidirectional': Any(),
                                                        },
                                                    },
                                                },
                                            },
                                            'mappings': {
                                                Any(): {
                                                    'eid_id': Any(),
                                                    'eid_address': {
                                                        'address_type': Any(),
                                                        'virtual_network_id': Any(),
                                                        'ipv4': {
                                                            'ipv4': Any(),
                                                        },
                                                        'ipv4_prefix': {
                                                            'ipv4_prefix': Any(),
                                                        },
                                                        'ipv6': {
                                                            'ipv6': Any(),
                                                        },
                                                        'ipv6_prefix': {
                                                            'ipv6_prefix': Any(),
                                                        },
                                                    },
                                                    'site_id': Any(),
                                                    'more_specifics_accepted': Any(),
                                                    'mapping_expiration_timeout': Any(),
                                                    'mapping_records': {
                                                        Any(): {
                                                            'xtr_id': Any(),
                                                            'site_id': Any(),
                                                            'eid': {
                                                                'address_type': Any(),
                                                                'virtual_network_id': Any(),
                                                                'ipv4': {
                                                                    'ipv4': Any(),
                                                                },
                                                                'ipv4_prefix': {
                                                                    'ipv4_prefix': Any(),
                                                                },
                                                                'ipv6': {
                                                                    'ipv6': Any(),
                                                                },
                                                                'ipv6_prefix': {
                                                                    'ipv6_prefix': Any(),
                                                                },
                                                            },
                                                            'time_to_live': Any(),
                                                            'creation_time': Any(),
                                                            'authoritative': Any(),
                                                            'static': Any(),
                                                            'negative_mapping': {
                                                                'map_reply_action': Any(),
                                                            },
                                                            'positive_mapping': {
                                                                'rlocs': {
                                                                    Any(): {
                                                                        'id': Any(),
                                                                        'locator_address': {
                                                                            'address_type': Any(),
                                                                            'virtual_network_id': Any(),
                                                                            'ipv4': {
                                                                                'ipv4': Any(),
                                                                            },
                                                                            'ipv4_prefix': {
                                                                                'ipv4_prefix': Any(),
                                                                            },
                                                                            'ipv6': {
                                                                                'ipv6': Any(),
                                                                            },
                                                                            'ipv6_prefix': {
                                                                                'ipv6_prefix': Any(),
                                                                            },
                                                                        },
                                                                        'priority': Any(),
                                                                        'weight': Any(),
                                                                        'multicast_priority': Any(),
                                                                        'multicast_weight': Any(),
                                                                    },
                                                                },
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                            'counters': {
                                                'map_registers_in': Any(),
                                                'map_registers_in_auth_failed': Any(),
                                                'map_notify_records_out': Any(),
                                                'proxy_reply_records_out': Any(),
                                                'map_requests_forwarded_out': Any(),
                                            },
                                        },
                                    },
                                    'mapping_system_type': Any(),
                                    'summary': {
                                        'number_configured_sites': Any(),
                                        'number_registered_sites': Any(),
                                        'af_datum': {
                                            Any(): {
                                                'address_type': Any(),
                                                'number_configured_eids': Any(),
                                                'number_registered_eids': Any(),
                                            },
                                        },
                                    },
                                    'counters': {
                                        'map_registers_in': Any(),
                                        'map_registers_in_auth_failed': Any(),
                                        'map_notify_records_out': Any(),
                                        'proxy_reply_records_out': Any(),
                                        'map_requests_forwarded_out': Any(),
                                    },
                                },
                                'map_resolver': {
                                    'enabled': Any(),
                                    'mapping_system_type': Any(),
                                    'ms_address': Any(),
                                },
                                'itr': {
                                    'enabled': Any(),
                                    'rloc_probing': {
                                        'interval': Any(),
                                        'retries': Any(),
                                        'retries_interval': Any(),
                                    },
                                    'itr_rlocs': Any(),
                                    'map_resolvers': {
                                        Any(): {
                                            'map_resolver': Any(),
                                        },
                                    },
                                    'proxy_itrs': {
                                        Any(): {
                                            'proxy_etr_address': Any(),
                                        },
                                    },
                                    'map_cache': {
                                        Any(): {
                                            'vni': Any(),
                                            'mappings': {
                                                Any(): {
                                                    'id': Any(),
                                                    'eid': {
                                                        'address_type': Any(),
                                                        'vrf': Any(),
                                                        'ipv4': {
                                                            'ipv4': Any(),
                                                        },
                                                        'ipv4_prefix': {
                                                            'ipv4_prefix': Any(),
                                                        },
                                                        'ipv6': {
                                                            'ipv6': Any(),
                                                        },
                                                        'ipv6_prefix': {
                                                            'ipv6_prefix': Any(),
                                                        },
                                                    },
                                                    'time_to_live': Any(),
                                                    'creation_time': Any(),
                                                    'authoritative': Any(),
                                                    'static': Any(),
                                                    'negative_mapping': {
                                                        'map_reply_action': Any(),
                                                    },
                                                    'positive_mapping': {
                                                        'rlocs': {
                                                            Any(): {
                                                                'id': Any(),
                                                                'locator_address': {
                                                                    'address_type': Any(),
                                                                    'virtual_network_id': Any(),
                                                                    'ipv4': {
                                                                        'ipv4': Any(),
                                                                    },
                                                                    'ipv4_prefix': {
                                                                        'ipv4_prefix': Any(),
                                                                    },
                                                                    'ipv6': {
                                                                        'ipv6': Any(),
                                                                    },
                                                                    'ipv6_prefix': {
                                                                        'ipv6_prefix': Any(),
                                                                    },
                                                                },
                                                                'priority': Any(),
                                                                'weight': Any(),
                                                                'multicast_priority': Any(),
                                                                'multicast_weight': Any(),
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                                'etr': {
                                    'encapsulation': Any(),
                                    'enabled': Any(),
                                    'mapping_servers': {
                                        Any(): {
                                            'ms_address': Any(),
                                            'auth_key': Any(),
                                            'auth_key_type': Any(),
                                        },
                                    },
                                    'local_eids': {
                                        Any(): {
                                            'vni': Any(),
                                            'use_petrs': {
                                                Any(): {
                                                    'use_petr': Any(),
                                                    'priority': Any(),
                                                    'weight': Any(),
                                                },
                                            },
                                            'dynamic_eids': {
                                                Any(): {
                                                    'id': Any(),
                                                    'eid_address': {
                                                        'address_type': Any(),
                                                        'vrf': Any(),
                                                        'ipv4': {
                                                            'ipv4': Any(),
                                                        },
                                                        'ipv4_prefix': {
                                                            'ipv4_prefix': Any(),
                                                        },
                                                        'ipv6': {
                                                            'ipv6': Any(),
                                                        },
                                                        'ipv6_prefix': {
                                                            'ipv6_prefix': Any(),
                                                        },
                                                    },
                                                    'rlocs': Any(),
                                                    'loopback_address': Any(),
                                                    'priority': Any(),
                                                    'weight': Any(),
                                                    'record_ttl': Any(),
                                                    'want_map_notify': Any(),
                                                    'proxy_reply': Any(),
                                                    'registration_interval': Any(),
                                                },
                                            },
                                            'eids': {
                                                Any(): {
                                                    'id': Any(),
                                                    'eid_address': {
                                                        'address_type': Any(),
                                                        'vrf': Any(),
                                                        'ipv4': {
                                                            'ipv4': Any(),
                                                        },
                                                        'ipv4_prefix': {
                                                            'ipv4_prefix': Any(),
                                                        },
                                                        'ipv6': {
                                                            'ipv6': Any(),
                                                        },
                                                        'ipv6_prefix': {
                                                            'ipv6_prefix': Any(),
                                                        },
                                                    },
                                                    'rlocs': Any(),
                                                    'loopback_address': Any(),
                                                    'priority': Any(),
                                                    'weight': Any(),
                                                    'record_ttl': Any(),
                                                    'want_map_notify': Any(),
                                                    'proxy_reply': Any(),
                                                    'registration_interval': Any(),
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'lldp': {
            'info': {
                'enabled': Any(),
                'hello_timer': Any(),
                'hold_timer': Any(),
                'suppress_tlv_advertisement': {
                    'chassis_id': Any(),
                    'port_id': Any(),
                    'port_description': Any(),
                    'system_name': Any(),
                    'system_description': Any(),
                    'system_capabilities': Any(),
                    'management_address': Any(),
                },
                'system_name': Any(),
                'system_description': Any(),
                'chassis_id': Any(),
                'chassis_id_type': Any(),
                'counters': {
                    'frame_in': Any(),
                    'frame_out': Any(),
                    'frame_error_in': Any(),
                    'frame_discard': Any(),
                    'tlv_discard': Any(),
                    'tlv_unknown': Any(),
                    'last_clear': Any(),
                    'tlv_accepted': Any(),
                    'entries_aged_out': Any(),
                },
                'interfaces': {
                    Any(): {
                        'if_name': Any(),
                        'enabled': Any(),
                        'counters': {
                            'frame_in': Any(),
                            'frame_out': Any(),
                            'frame_error_in': Any(),
                            'frame_discard': Any(),
                            'tlv_discard': Any(),
                            'tlv_unknown': Any(),
                            'last_clear': Any(),
                            'frame_error_out': Any(),
                        },
                        'port_id': {
                            Any(): {
                                'neighbors': {
                                    Any(): {
                                        'neighbor_id': Any(),
                                        'system_name': Any(),
                                        'system_description': Any(),
                                        'chassis_id': Any(),
                                        'chassis_id_type': Any(),
                                        'id': Any(),
                                        'age': Any(),
                                        'last_update': Any(),
                                        'port_id': Any(),
                                        'port_id_type': Any(),
                                        'port_description': Any(),
                                        'management_address': Any(),
                                        'management_address_v6': Any(),
                                        'management_address_type': Any(),
                                        'custom_tlvs': {
                                            Any(): {
                                                'type': Any(),
                                                'oui': Any(),
                                                'oui_subtype': Any(),
                                                'value': Any(),
                                            },
                                        },
                                        'capabilities': {
                                            Any(): {
                                                'name': Any(),
                                                'enabled': Any(),
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'mcast': {
            'info': {
                'vrf': {
                    Any(): {
                        'address_family': {
                            Any(): {
                                'enable': Any(),
                                'multipath': Any(),
                                'mroute': {
                                    Any(): {
                                        'path': {
                                            Any(): {
                                                'neighbor_address': Any(),
                                                'interface_name': Any(),
                                                'admin_distance': Any(),
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            'table': {
                'vrf': {
                    Any(): {
                        'address_family': {
                            Any(): {
                                'multicast_group': {
                                    Any(): {
                                        'source-address': { 
                                            Any(): {
                                                'flags': Any(),
                                                'uptime': Any(),
                                                'expire': Any(),
                                                'rp': Any(),
                                                'rpf_nbr': Any(),
                                                'incoming_interface_list': {
                                                    Any(): {
                                                        'rpf_nbr': Any(),
                                                        'rpf_info': Any(),
                                                    },
                                                },
                                                'outgoing_interface_list': {
                                                    Any(): {
                                                        'state_mode': Any(),
                                                        'uptime': Any(),
                                                        'expire': Any(),
                                                        'flags': Any(),
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'mld': {
            'info': {
                'vrfs': {
                    Any(): {
                        'max_groups': Any(),
                        'groups_count': Any(),
                        'ssm_map': {
                            Any(): {
                                'source_addr': Any(),
                                'group_policy': Any(),
                                'group_range': Any(),
                                'group_address': Any(),
                            },
                        },
                        'interfaces': {
                            Any(): {
                                'enable': Any(),
                                'group_policy': Any(),
                                'immediate_leave': Any(),
                                'max_groups': Any(),
                                'query_interval': Any(),
                                'query_max_response_time': Any(),
                                'robustness_variable': Any(),
                                'version': Any(),
                                'oper_status': Any(),
                                'querier': Any(),
                                'joined_group': Any(),
                                'join_group': {
                                    Any(): {
                                        'group': Any(),
                                        'source': Any(),
                                    },
                                },
                                'static_group': {
                                    Any(): {
                                        'group': Any(),
                                        'source': Any(),
                                    },
                                },
                                'group': {
                                    Any(): {
                                        'expire': Any(),
                                        'filter_mode': Any(),
                                        'host_count': Any(),
                                        'up_time': Any(),
                                        'host': Any(),
                                        'last_reporter': Any(),
                                        'source': {
                                            Any(): {
                                                'expire': Any(),
                                                'up_time': Any(),
                                                'last_reporter': Any(),
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'msdp': {
            'info': {
                'vrf': {
                    Any(): {
                        'global': {
                            'connect_source': Any(),
                            'default_peer': {
                                'peer_addr': Any(),
                                'prefix_policy': Any(),
                            },
                            'originating_rp': Any(),
                            'local_as': Any(),
                            'originator_id': Any(),
                            'statistics': {
                                'num_of_configured_peers': Any(),
                                'num_of_established_peers': Any(),
                                'num_of_shutdown_peers': Any(),
                            },
                            'sa_filter': {
                                'in': Any(),
                                'out': Any(),
                            },
                            'sa_limit': Any(),
                            'ttl_threshold': Any(),
                            'timer': {
                                'connect_retry_interval': Any(),
                            },
                        },
                        'peer': {
                            Any(): {
                                'connect_source': Any(),
                                'peer_as': Any(),
                                'authentication': {
                                    'password': {
                                        'key': Any(),
                                    },
                                },
                                'enable': Any(),
                                'description': Any(),
                                'mesh_group': Any(),
                                'sa_filter': {
                                    'in': Any(),
                                    'out': Any(),
                                },
                                'sa_limit': Any(),
                                'timer': {
                                    'connect_retry_interval': Any(),
                                    'keepalive_interval': Any(),
                                    'holdtime_interval': Any(),
                                },
                                'ttl_threshold': Any(),
                                'session_state': Any(),
                                'elapsed_time': Any(),
                                'is_default_peer': Any(),
                                'statistics': {
                                    'last_message_received': Any(),
                                    'num_of_sg_received': Any(),
                                    'discontinuity_time': Any(),
                                    'error': {
                                        'rpf_failure': Any(),
                                    },
                                    'queue': {
                                        'size_in': Any(),
                                        'size_out': Any(),
                                    },
                                    'received': {
                                        'keepalive': Any(),
                                        'notification': Any(),
                                        'sa_message': Any(),
                                        'sa_response': Any(),
                                        'sa_request': Any(),
                                        'total': Any(),
                                    },
                                    'sent': {
                                        'keepalive': Any(),
                                        'notification': Any(),
                                        'sa_message': Any(),
                                        'sa_response': Any(),
                                        'sa_request': Any(),
                                        'total': Any(),
                                    },
                                    'sa_policy': {
                                        'in': {
                                            'total_accept_count': Any(),
                                            'total_reject_count': Any(),
                                            Any(): {
                                                Any(): {
                                                    'num_of_comparison': Any(),
                                                    'num_of_matches': Any(),
                                                },
                                            },
                                        },
                                        'out': {
                                            'total_accept_count': Any(),
                                            'total_reject_count': Any(),
                                            Any(): {
                                                Any(): {
                                                    'num_of_comparison': Any(),
                                                    'num_of_matches': Any(),
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                        'sa_cache': {
                            Any(): {
                                'group': Any(),
                                'source_addr': Any(),
                                'origin_rp': {
                                    Any(): {
                                        'rp_address': Any(),
                                        'is_local_rp': Any(),
                                        'sa_adv_expire': Any(),
                                    },
                                },
                                'up_time': Any(),
                                'expire': Any(),
                                'holddown_interval': Any(),
                                'peer_learned_from': Any(),
                                'rpf_peer': Any(),
                            },
                        },
                    },
                },
            },
        },

        'nd': {
            'info': {
                'interfaces': {
                    Any(): {
                        'interface': Any(),
                        'router_advertisement': {
                            'interval': Any(),
                            'lifetime': Any(),
                            'suppress': Any(),
                        },
                        'neighbors': {
                            Any(): {
                                'ip': Any(),
                                'link_layer_address': Any(),
                                'origin': Any(),
                                'is_router': Any(),
                                'neighbor_state': Any(),
                                'age': Any(),
                            },
                        },
                    },
                },
            },
        },

        'ntp': {
        },

        'ospf': {
            'info': {
                'feature_ospf': Any(),
                'vrf': {
                    Any(): {
                        'address_family': {
                            Any(): {
                                'instance': {
                                    Any(): {
                                        'router_id': Any(),
                                        'maximum_interfaces': Any(),
                                        'preference': {
                                            'single_value': {
                                                'all': Any(),
                                            },
                                            'multi_values': {
                                                'granularity': {
                                                    'detail': {
                                                        'intra_area': Any(),
                                                        'inter_area': Any(),
                                                    },
                                                    'coarse': {
                                                        'internal': Any(),
                                                    },
                                                },
                                                'external': Any(),
                                            },
                                        },
                                        'redistribution': {
                                            'max_prefix': {
                                                'num_of_prefix': Any(),
                                                'prefix_thld': Any(),
                                                'warn_only': Any(),
                                            },
                                            'bgp': {
                                                'bgp_id': Any(),
                                                'metric': Any(),
                                                'metric_type': Any(),
                                                'nssa_only': Any(),
                                                'route_map': Any(),
                                                'subnets': Any(),
                                                'tag': Any(),
                                                'lsa_type_summary': Any(),
                                                'preserve_med': Any(),
                                            },
                                            'connected': {
                                                'enabled': Any(),
                                                'metric': Any(),
                                                'route_policy': Any(),
                                            },
                                            'static': {
                                                'enabled': Any(),
                                                'metric': Any(),
                                                'route_policy': Any(),
                                            },
                                            'isis': {
                                                'isis_pid': Any(),
                                                'metric': Any(),
                                                'route_policy': Any(),
                                            },
                                        },
                                        'nsr': {
                                            'enable': Any(),
                                        },
                                        'graceful_restart': {
                                            Any(): {
                                                'enable': Any(),
                                                'type': Any(),
                                                'helper_enable': Any(),
                                                'restart_interval': Any(),
                                                'helper_strict_lsa_checking': Any(),
                                            },
                                        },
                                        'enable': Any(),
                                        'auto_cost': {
                                            'enable': Any(),
                                            'reference_bandwidth': Any(),
                                        },
                                        'spf_control': {
                                            'paths': Any(),
                                            'throttle': {
                                                'spf': {
                                                    'start': Any(),
                                                    'hold': Any(),
                                                    'maximum': Any(),
                                                },
                                                'lsa': {
                                                    'start': Any(),
                                                    'hold': Any(),
                                                    'maximum': Any(),
                                                },
                                            },
                                        },
                                        'database_control': {
                                            'max_lsa': Any(),
                                        },
                                        'stub_router': {
                                            'always': {
                                                'always': Any(),
                                                'include_stub': Any(),
                                                'summary_lsa': Any(),
                                                'external_lsa': Any(),
                                            },
                                            'on_startup': {
                                                'on_startup': Any(),
                                                'include_stub': Any(),
                                                'summary_lsa': Any(),
                                                'external_lsa': Any(),
                                            },
                                            'on_switchover': {
                                                'on_switchover': Any(),
                                                'include_stub': Any(),
                                                'summary_lsa': Any(),
                                                'external_lsa': Any(),
                                            },
                                        },
                                        'default_originate': {
                                            'default_originate': Any(),
                                            'always': Any(),
                                        },
                                        'mpls': {
                                            'te': {
                                                'router_id': Any(),
                                            },
                                            'ldp': {
                                                'autoconfig': Any(),
                                                'autoconfig_area_id': Any(),
                                                'igp_sync': Any(),
                                            },
                                        },
                                        'local_rib': {
                                            Any(): {
                                                'prefix': Any(),
                                                'next_hops': {
                                                    'next_hop': {
                                                        'outgoing_interface': Any(),
                                                        'next_hop': Any(),
                                                    },
                                                },
                                                'metric': Any(),
                                                'route_type': Any(),
                                                'route_tag': Any(),
                                            },
                                        },
             
                                        'bfd': {
                                            'enable': Any(),
                                            'strict_mode': Any(),
                                        },
                                        'log_adjacency_changes': {
                                            'enable': Any(),
                                            'detail': Any(),
                                        },
                                        'adjacency_stagger': {
                                            'initial_number': Any(),
                                            'maximum_number': Any(),
                                            'disable': Any(),
                                            'no_initial_limit': Any(),
                                        },
                                        'areas': {
                                            Any(): {
                                                'area_id': Any(),
                                                'area_type': Any(),
                                                'summary': Any(),
                                                'default_cost': Any(),
                                                'bfd': {
                                                    'enable': Any(),
                                                    'minimum_interval': Any(),
                                                    'multiplier': Any(),
                                                },
                                                'enabled_networks': {
                                                    Any(): {
                                                        'network': Any(),
                                                        'wildcard': Any(),
                                                    },
                                                },
                                                'mpls': {
                                                    'te': {
                                                        'enable': Any(),
                                                    },
                                                    'ldp': {
                                                        'auto_config': Any(),
                                                        'sync': Any(),
                                                        'sync_igp_shortcuts': Any(),
                                                    },
                                                },
                                                'ranges': {
                                                    Any(): {
                                                        'prefix': Any(),
                                                        'advertise': Any(),
                                                        'cost': Any(),
                                                    },
                                                },
                                                'statistics': {
                                                    'spf_runs_count': Any(),
                                                    'abr_count': Any(),
                                                    'asbr_count': Any(),
                                                    'as_nssa_translator_event_count': Any(),
                                                    'area_scope_lsa_count': Any(),
                                                    'area_scope_lsa_cksum_sum': Any(),
                                                },
                                                'database': {
                                                    'lsa_types': {
                                                        Any(): {
                                                            'lsa_type': Any(),
                                                            'lsas': {
                                                                Any(): {
                                                                    'lsa_id': Any(),
                                                                    'adv_router': Any(),
                                                                    'decoded_completed': Any(),
                                                                    'raw_data': Any(),
                                                                    'ospfv2': {
                                                                        'header': {
                                                                            'option': Any(),
                                                                            'lsa_id': Any(),
                                                                            'opaque_type': Any(),
                                                                            'opaque_id': Any(),
                                                                            'age': Any(),
                                                                            'type': Any(),
                                                                            'adv_router': Any(),
                                                                            'seq_num': Any(),
                                                                            'checksum': Any(),
                                                                            'length': Any(),
                                                                        },
                                                                        'body': {
                                                                            'router': {
                                                                                'flags': Any(),
                                                                                'num_of_links': Any(),
                                                                                'links': {
                                                                                    Any(): {
                                                                                        'link_id': Any(),
                                                                                        'link_data': Any(),
                                                                                        'type': Any(),
                                                                                        'topologies': {
                                                                                            Any(): {
                                                                                                'topology': Any(),
                                                                                                'mt_id': Any(),
                                                                                                'metric': Any(),
                                                                                            },
                                                                                        },
                                                                                    },
                                                                                },
                                                                            },
                                                                            'network': {
                                                                                'network_mask': Any(),
                                                                                'attached_routers': {
                                                                                    Any(): {},
                                                                                },
                                                                            },
                                                                            'summary': {
                                                                                'network_mask': Any(),
                                                                                'topologies': {
                                                                                    Any(): {
                                                                                        'topology': Any(),
                                                                                        'mt_id': Any(),
                                                                                        'metric': Any(),
                                                                                    },
                                                                                },
                                                                            },
                                                                            'external': {
                                                                                'network_mask': Any(),
                                                                                'topologies': {
                                                                                    Any(): {
                                                                                        'topology': Any(),
                                                                                        'mt_id': Any(),
                                                                                        'flags': Any(),
                                                                                        'metric': Any(),
                                                                                        'forwarding_address': Any(),
                                                                                        'external_route_tag': Any(),
                                                                                    },
                                                                                },
                                                                            },
                                                                            'opaque': {
                                                                                'unknown_tlvs': {
                                                                                    Any(): {
                                                                                        'type': Any(),
                                                                                        'length': Any(),
                                                                                        'value': Any(),
                                                                                    },
                                                                                },
                                                                                'node_tag_tlvs': {
                                                                                    Any(): {
                                                                                        Any(): {
                                                                                            'tag': Any(),
                                                                                        },
                                                                                    },
                                                                                },
                                                                                'router_address_tlv': {
                                                                                    'router_address': Any(),
                                                                                },
                                                                                'link_tlvs': {
                                                                                    Any(): {
                                                                                        'link_type': Any(),
                                                                                        'link_id': Any(),
                                                                                        'link_name': Any(),
                                                                                        'local_if_ipv4_addrs': {
                                                                                            Any(): {},
                                                                                        },
                                                                                        'remote_if_ipv4_addrs': {
                                                                                            Any(): {},
                                                                                        },
                                                                                        'te_metric': Any(),
                                                                                        'max_bandwidth': Any(),
                                                                                        'max_reservable_bandwidth': Any(),
                                                                                        'unreserved_bandwidths': {
                                                                                            Any(): {
                                                                                                'priority': Any(),
                                                                                                'unreserved_bandwidth': Any(),
                                                                                            },
                                                                                        },
                                                                                        'admin_group': Any(),
                                                                                        'unknown_tlvs': {
                                                                                            Any(): {
                                                                                                'type': Any(),
                                                                                                'length': Any(),
                                                                                                'value': Any(),
                                                                                            },
                                                                                        },
                                                                                    },
                                                                                    'extended_prefix_tlvs': {
                                                                                        Any(): {
                                                                                            'route_type': Any(),
                                                                                            'flags': Any(),
                                                                                            'prefix': Any(),
                                                                                            'unknown_tlvs': {
                                                                                                Any(): {
                                                                                                    'type': Any(),
                                                                                                    'length': Any(),
                                                                                                    'value': Any(),
                                                                                                },
                                                                                            },
                                                                                        },
                                                                                    },
                                                                                    'extended_link_tlvs': {
                                                                                        Any(): {
                                                                                            'link_id': Any(),
                                                                                            'link_data': Any(),
                                                                                            'type': Any(),
                                                                                            'unknown_tlvs': {
                                                                                                Any(): {
                                                                                                    'type': Any(),
                                                                                                    'length': Any(),
                                                                                                    'value': Any(),
                                                                                                },
                                                                                            },
                                                                                        },
                                                                                    },
                                                                                },
                                                                            },
                                                                        },
                                                                    },
                                                                },
                                                            },
                                                        },
                                                    },
                                                },
                                                'virtual_links': {
                                                    Any(): {
                                                        'name': Any(),
                                                        'transit_area_id': Any(),
                                                        'router_id': Any(),
                                                        'hello_interval': Any(),
                                                        'dead_interval': Any(),
                                                        'retransmit_interval': Any(),
                                                        'transmit_delay': Any(),
                                                        'demand_circuit': Any(),
                                                        'ttl_secutiry': {
                                                            'enable': Any(),
                                                            'hops': Any(),
                                                        },
                                                        'authentication': {
                                                            'auth_trailer_key_chain': {
                                                                'key_chain': Any(),
                                                            },
                                                            'auth_trailer_key': {
                                                                'key': Any(),
                                                                'crypto_algorithm': Any(),
                                                            },
                                                        },
                                                        'cost': Any(),
                                                        'state': Any(),
                                                        'hello_timer': Any(),
                                                        'wait_timer': Any(),
                                                        'dr_router_id': Any(),
                                                        'dr_ip_addr': Any(),
                                                        'bdr_router_id': Any(),
                                                        'bdr_ip_addr': Any(),
                                                        'statistics': {
                                                            'if_event_count': Any(),
                                                            'link_scope_lsa_count': Any(),
                                                            'link_scope_lsa_cksum_sum': Any(),
                                                            'database': {
                                                                Any(): {
                                                                    'lsa_type': Any(),
                                                                    'lsa_count': Any(),
                                                                    'lsa_chksum_sum': Any(),
                                                                },
                                                            },
                                                        },
                                                        'neighbors': {
                                                            Any(): {
                                                                'neighbor_router_id': Any(),
                                                                'address': Any(),
                                                                'dr_router_id': Any(),
                                                                'dr_ip_addr': Any(),
                                                                'bdr_router_id': Any(),
                                                                'bdr_ip_addr': Any(),
                                                                'state': Any(),
                                                                'last_state_change': Any(),
                                                                'dead_tiemr': Any(),
                                                                'statistics': {
                                                                    'nbr_event_count': Any(),
                                                                    'nbr_retrans_qlen': Any(),
                                                                },
                                                            },
                                                        },
                                                    },
                                                },
                                                'sham_links': {
                                                    Any(): {
                                                        'name': Any(),
                                                        'local_id': Any(),
                                                        'remote_id': Any(),
                                                        'transit_area_id': Any(),
                                                        'hello_interval': Any(),
                                                        'dead_interval': Any(),
                                                        'retransmit_interval': Any(),
                                                        'transmit_delay': Any(),
                                                        'demand_circuit': Any(),
                                                        'ttl_secutiry': {
                                                            'enable': Any(),
                                                            'hops': Any(),
                                                        },
                                                        'authentication': {
                                                            'auth_trailer_key_chain': {
                                                                'key_chain': Any(),
                                                            },
                                                            'auth_trailer_key': {
                                                                'key': Any(),
                                                                'crypto_algorithm': Any(),
                                                            },
                                                        },
                                                        'cost': Any(),
                                                        'prefix_suppression': Any(),
                                                        'state': Any(),
                                                        'hello_timer': Any(),
                                                        'wait_timer': Any(),
                                                        'dr_router_id': Any(),
                                                        'dr_ip_addr': Any(),
                                                        'bdr_router_id': Any(),
                                                        'bdr_ip_addr': Any(),
                                                        'statistics': {
                                                            'if_event_count': Any(),
                                                            'link_scope_lsa_count': Any(),
                                                            'link_scope_lsa_cksum_sum': Any(),
                                                            'database': {
                                                                Any(): {
                                                                    'lsa_type': Any(),
                                                                    'lsa_count': Any(),
                                                                    'lsa_chksum_sum': Any(),
                                                                },
                                                            },
                                                        },
                                                        'neighbors': {
                                                            Any(): {
                                                                'neighbor_router_id': Any(),
                                                                'address': Any(),
                                                                'dr_router_id': Any(),
                                                                'dr_ip_addr': Any(),
                                                                'bdr_router_id': Any(),
                                                                'bdr_ip_addr': Any(),
                                                                'state': Any(),
                                                                'last_state_change': Any(),
                                                                'dead_tiemr': Any(),
                                                                'statistics': {
                                                                    'nbr_event_count': Any(),
                                                                    'nbr_retrans_qlen': Any(),
                                                                },
                                                            },
                                                        },
                                                    },
                                                },
                                                'passive': Any(),
                                                'mtu_ignore': Any(),
                                                'demand_circuit': Any(),
                                                'external_out': Any(),
                                                'flood_reduction': Any(),
                                                'link_down_fast_detect': Any(),
                                                'interfaces': {
                                                    Any(): {
                                                        'name': Any(),
                                                        'interface_type': Any(),
                                                        'passive': Any(),
                                                        'demand_circuit': Any(),
                                                        'priority': Any(),
                                                        'transmit_delay': Any(),
                                                        'static_neigbhors': {
                                                            Any(): {
                                                                'identifier': Any(),
                                                                'cost': Any(),
                                                                'poll_interval': Any(),
                                                                'priority': Any(),
                                                            },
                                                        },
                                                        'bfd': {
                                                            'enable': Any(),
                                                            'interval': Any(),
                                                            'min_interval': Any(),
                                                            'multiplier': Any(),
                                                        },
                                                        'hello_interval': Any(),
                                                        'dead_interval': Any(),
                                                        'retransmit_interval': Any(),
                                                        'lls': Any(),
                                                        'ttl_secutiry': {
                                                            'enable': Any(),
                                                            'hops': Any(),
                                                        },
                                                        'enable': Any(),
                                                        'authentication': {
                                                            'auth_trailer_key_chain': {
                                                                'key_chain': Any(),
                                                            },
                                                            'auth_trailer_key': {
                                                                'key': Any(),
                                                                'crypto_algorithm': Any(),
                                                            },
                                                        },
                                                        'cost': Any(),
                                                        'mtu_ignore': Any(),
                                                        'prefix_suppression': Any(),
                                                        'state': Any(),
                                                        'hello_timer': Any(),
                                                        'wait_timer': Any(),
                                                        'dr_router_id': Any(),
                                                        'dr_ip_addr': Any(),
                                                        'bdr_router_id': Any(),
                                                        'bdr_ip_addr': Any(),
                                                        'statistics': {
                                                            'if_event_count': Any(),
                                                            'link_scope_lsa_count': Any(),
                                                            'link_scope_lsa_cksum_sum': Any(),
                                                            'database': {
                                                                Any(): {
                                                                    'lsa_type': Any(),
                                                                    'lsa_count': Any(),
                                                                    'lsa_chksum_sum': Any(),
                                                                },
                                                            },
                                                        },
                                                        'neighbors': {
                                                            Any(): {
                                                                'neighbor_router_id': Any(),
                                                                'address': Any(),
                                                                'dr_router_id': Any(),
                                                                'dr_ip_addr': Any(),
                                                                'bdr_router_id': Any(),
                                                                'bdr_ip_addr': Any(),
                                                                'state': Any(),
                                                                'last_state_change': Any(),
                                                                'dead_tiemr': Any(),
                                                                'statistics': {
                                                                    'nbr_event_count': Any(),
                                                                    'nbr_retrans_qlen': Any(),
                                                                },
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'pim': {
            'info': {
                'feature_pim': Any(),
                'feature_pim6': Any(),
                'vrf': {
                    Any(): {
                        'address_family': {
                            Any(): {
                                'topology_tree_info': {
                                    Any(): {
                                        'group': Any(),
                                        'source_address': Any(),
                                        'is_rpt': Any(),
                                        'expiration': Any(),
                                        'incoming_interface': Any(),
                                        'mode': Any(),
                                        'msdp_learned': Any(),
                                        'rp_address': Any(),
                                        'rpf_neighbor': Any(),
                                        'spt_bit': Any(),
                                        'up_time': Any(),
                                        'outgoing_interface': {
                                            Any(): {
                                                'expiration': Any(),
                                                'up_time': Any(),
                                                'jp_state': Any(),
                                            },
                                        },
                                    },
                                },
                                'rp': {
                                    'static_rp': {
                                        Any(): {
                                            'sm': {
                                                'policy-name': Any(),
                                                'override': Any(),
                                                'policy': Any(),
                                                'prefix_list': Any(),
                                                'route_map': Any(),
                                            },
                                            'bidir': {
                                                'policy_name': Any(),
                                                'override': Any(),
                                                'policy': Any(),
                                                'prefix_list': Any(),
                                                'route_map': Any(),
                                            },
                                        },
                                    },
                                    'autorp': {
                                        'send_rp_announce': {
                                            'interface': Any(),
                                            'group': Any(),
                                            'scope': Any(),
                                            'group_list': Any(),
                                            'route-map': Any(),
                                            'prefix_list': Any(),
                                            'interval': Any(),
                                            'bidir': Any(),
                                        },
                                        'send_rp_discovery': {
                                            'interface': Any(),
                                            'scope': Any(),
                                        },
                                        'listener': Any(),
                                    },
                                    'bsr': {
                                        'bsr_candidate': {
                                            'if_name or address': Any(),
                                            'hash_mask_length': Any(),
                                            'priority': Any(),
                                            'accept_rp_acl': Any(),
                                        },
                                        Any(): {
                                            'interface': Any(),
                                            'address': Any(),
                                            'policy': Any(),
                                            'mode': Any(),
                                            'priority': Any(),
                                            'interval': Any(),
                                            'route_map': Any(),
                                            'prefix_list': Any(),
                                        },
                                        'bsr': {
                                            'address': Any(),
                                            'hash_mask_length': Any(),
                                            'priority': Any(),
                                            'up_time': Any(),
                                            'expires': Any(),
                                        },
                                        'election_state': {
                                            'bsr_election_state': Any(),
                                        },
                                        'bsr_next_bootstrap': Any(),
                                        'rp': {
                                            'rp_address': Any(),
                                            'group_policy': Any(),
                                            'up_time': Any(),
                                        },
                                        'rp_candidate_next_advertisement': Any(),
                                    },
                                    'rp_list': {
                                        Any(): {
                                            'address': Any(),
                                            'mode': Any(),
                                            'info_source_address': Any(),
                                            'info_source_type': Any(),
                                            'up_time': Any(),
                                            'expiration': Any(),
                                        },
                                    },
                                    'rp_mappings': {
                                        Any(): {
                                            'group': Any(),
                                            'rp_address': Any(),
                                            'protocol': Any(),
                                            'up_time': Any(),
                                            'expiration': Any(),
                                        },
                                    },
                                    'bidir': {
                                        'df_election': {
                                            'offer_interval': Any(),
                                            'backoff_interval': Any(),
                                            'offer_multiplier': Any(),
                                        },
                                        'interface_df_election': {
                                            Any(): {
                                                'address': Any(),
                                                'interface_name': Any(),
                                                'df_address': Any(),
                                                'interface_state': Any(),
                                            },
                                        },
                                    },
                                },
                                'sm': {
                                    'asm': {
                                        'anycast_rp': {
                                            Any(): {
                                                'anycast_address': Any(),
                                            },
                                        },
                                        'spt_switch': {
                                            Any(): {
                                                'policy_name': Any(),
                                            },
                                        },
                                        'accept_register': Any(),
                                        'register_source': Any(),
                                        'sg_expiry_timer': {
                                            'sg_list': Any(),
                                            'prefix_list': Any(),
                                            'infinity': Any(),
                                        },                           
                                    },
                                    'ssm': {
                                        Any(): {},
                                    },
                                },
                                'dm': {},
                                'bidir': {},
                                'log_neighbor_changes': Any(),
                            },
                        },
                        'interfaces': {
                            Any(): {
                                'address_family': {
                                    Any(): {
                                        'bfd': {
                                            'enable': Any(),
                                        },
                                        'dr_priority': Any(),
                                        'hello_interval': Any(),
                                        'jp_interval': Any(),
                                        'propagation_delay': Any(),
                                        'override_interval': Any(),
                                        'address': Any(),
                                        'dr_address': Any(),
                                        'oper_status': Any(),
                                        'hello_expiration': Any(),
                                        'neighbors': {
                                            Any(): {
                                                'bfd_status': Any(),
                                                'expiration': Any(),
                                                'dr_priority': Any(),
                                                'gen_id': Any(),
                                                'up_time': Any(),
                                                'interface': Any(),
                                                'bidir_capable': Any(),
                                            },
                                        },
                                        'sm': {
                                            'passive': Any(),
                                        },
                                        'dm': {},
                                        'bidir': {
                                            'df_election': {
                                                'offer_interval': Any(),
                                                'backoff_interval': Any(),
                                                'offer_multiplier': Any(),
                                            },
                                        },
                                        'neighbor_filter': Any(),
                                        'bsr_border': Any(),
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'platform': {
            'chassis': Any(),
            'chassis_sn': Any(),
            'rtr_type': Any(),
            'os': Any(),
            'version': Any(),
            'image': Any(),
            'config_register': Any(),
            'main_mem': Any(),
            'dir': Any(),
            'redundancy_mode': Any(),
            'switchover_reason': Any(),
            'redundancy_communication': Any(),
            'swstack': Any(),
            'issu_rollback_timer_state': Any(),
            'issu_rollback_timer_reason': Any(),
            'virtual_device': {
                Any(): {
                    'name': Any(),
                    'status': Any(),
                    'membership': {
                        Any(): {
                            'type': Any(),
                            'status': Any(),
                        },
                    },
                },
            },
            'slot': {
                'rp': {
                    Any(): {
                        'name': Any(),
                        'state': Any(),
                        'swstack_role': Any(),
                        'redundancy_state': Any(),
                        'uptime': Any(),
                        'system_image': Any(),
                        'boot_image': Any(),
                        'config_register': Any(),
                        'sn': Any(),
                        'subslot': {
                            'subslot': {
                                'name': Any(),
                                'state' : Any(),
                                'sn' : Any(),
                            },
                        },
                        'issu': {
                            'in_progress': Any(),
                            'last_operation': Any(),
                            'terminal_state_reached': Any(),
                            'runversion_executed': Any(),
                        },
                    },
                },
                'lc': {
                    Any(): {
                        'name': Any(),
                        'state': Any(),
                        'sn': Any(),
                        'subslot': {
                            Any(): {
                                'name': Any(),
                                'state': Any(),
                                'sn': Any(),
                            },
                        },
                    },
                },
                'oc': {
                    Any(): {
                        'name': Any(),
                        'state': Any(),
                        'sn': Any(),
                    },
                },
            },
        },

        'prefix_list': {
            'info': {
                'prefix-set-name': {
                    Any(): {
                        'prefix-set-name': Any(),
                        'protocol': Any(),
                        'prefixes': {
                            Any(): {
                                'prefix': Any(),
                                'masklength-range': Any(),
                                'action': Any(),
                            },
                        },
                    },
                },
            },
        },

        'rip': {
            'info': {
                'vrf': {
                    Any(): {
                        'address_family': {
                            Any(): {
                                'instance': {
                                    Any(): {
                                        'originate_default_route': {
                                            'enabled': Any(),
                                            'route_policy': Any(),
                                        },
                                        'default_metric': Any(),
                                        'split_horizon': Any(),
                                        'poison_reverse': Any(),
                                        'distance': Any(),
                                        'triggered_update_threshold': Any(),
                                        'maximum_paths': Any(),
                                        'output_delay': Any(),
                                        'distribute_list': {
                                            Any(): {
                                                'direction': {
                                                    Any(): {
                                                        'if_name': Any(),
                                                    },
                                                },
                                            },
                                        },
                                        'redistribute': {
                                            'bgp': {
                                                Any(): {
                                                    'metric': Any(),
                                                    'route_policy': Any(),
                                                },
                                            },
                                            'cg_nat': {
                                                'metric': Any(),
                                                'route_policy': Any(),
                                            },
                                            'connected': {
                                                'metric': Any(),
                                                'route_policy': Any(),
                                            },
                                            'ipsec': {
                                                'metric': Any(),
                                                'route_policy': Any(),
                                            },
                                            'isis': {
                                                Any(): {
                                                    'level': Any(),
                                                    'metric': Any(),
                                                    'route_policy': Any(),
                                                },
                                            },
                                            'nat': {
                                                'metric': Any(),
                                                'route_policy': Any(),
                                            },
                                            'ospfv2': {
                                                Any(): {
                                                    'route_type': Any(),
                                                    'metric': Any(),
                                                    'route_policy': Any(),
                                                },
                                            },
                                            'ospfv3': {
                                                Any(): {
                                                    'route_type': Any(),
                                                    'metric': Any(),
                                                    'route_policy': Any(),
                                                },
                                            },
                                            'ripv2': {
                                                Any(): {
                                                    'metric': Any(),
                                                    'route_policy': Any(),
                                                },
                                            },
                                            'ripng': {
                                                Any(): {
                                                    'metric': Any(),
                                                    'route_policy': Any(),
                                                },
                                            },
                                            'static': {
                                                'metric': Any(),
                                                'route_policy': Any(),
                                            },
                                        },
                                        'timers': {
                                            'update_interval': Any(),
                                            'invalid_interval': Any(),
                                            'holddown_interval': Any(),
                                            'flush_interval': Any(),
                                        },
                                        'interfaces': {
                                            Any(): {
                                                'authentication': {
                                                    'auth_key_chain': {
                                                        'key_chain': Any(),
                                                    },
                                                    'auth_key': {
                                                        'key': Any(),
                                                        'crypto_algorithm': Any(),
                                                    },
                                                },
                                                'bfd': {
                                                    'enable': Any(),
                                                    'local_multiplier': Any(),
                                                    'interval_config_type': {
                                                        'tx_rx_intervals': {
                                                            'desired_min_tx_interval': Any(),
                                                            'required_min_rx_interval': Any(),
                                                        },
                                                        'single_interval': {
                                                            'min_interval': Any(),
                                                        },
                                                    },
                                                },
                                                'cost': Any(),
                                                'neighbors': {
                                                    Any(): {
                                                        'address': Any(),
                                                    },
                                                },
                                                'no_listen': Any(),
                                                'originate_default_route': {
                                                    'enabled': Any(),
                                                    'route_policy': Any(),
                                                },
                                                'passive': Any(),
                                                'split_horizon': Any(),
                                                'poison_reverse': Any(),
                                                'summary_address': {
                                                    Any(): {
                                                        'metric': Any(),
                                                    },
                                                },
                                                'timers': {
                                                    'update_interval': Any(),
                                                    'invalid_interval': Any(),
                                                    'holddown_interval': Any(),
                                                    'flush_interval': Any(),
                                                },
                                                'oper_status': Any(),
                                                'next_full_update': Any(),
                                                'valid_address': Any(),
                                                'statistics': {
                                                    'discontinuity_time': Any(),
                                                    'bad_packets_rcvd': Any(),
                                                    'bad_routes_rcvd': Any(),
                                                    'updates_sent': Any(),
                                                },
                                            },
                                        },
                                        'next_triggered_update': Any(),
                                        'num_of_routes': Any(),
                                        'neighbors': {
                                            Any(): {
                                                'last_update': Any(),
                                                'bad_packets_rcvd': Any(),
                                                'bad_routes_rcvd': Any(),
                                            },
                                        },
                                        'routes': {
                                            Any(): {
                                                'index': {
                                                      Any(): {
                                                            'next_hop': Any(),
                                                            'interface': Any(),
                                                            'redistributed': Any(),
                                                            'route_type': Any(),
                                                            'summary_type': Any(),
                                                            'metric': Any(),
                                                            'expire_time': Any(),
                                                            'deleted': Any(),
                                                            'holddown': Any(),
                                                            'need_triggered_update': Any(),
                                                            'inactive': Any(),
                                                            'flush_expire_before_holddown': Any(),
                                                      },
                                                },
                                            },
                                        },
                                        'statistics': {
                                            'discontinuity_time': Any(),
                                            'requests_rcvd': Any(),
                                            'requests_sent': Any(),
                                            'responses_rcvd': Any(),
                                            'responses_sent': Any(),
                                        },                                       
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'route_policy': {
            'info': {
                Any(): {
                    'statements': {
                        'description': Any(),
                        Any(): {
                            'conditions': {
            
                                'match_med_eq': Any(),
                                'match_origin_eq': Any(),
                                'match_nexthop_in': Any(),
                                'match_nexthop_in_v6': Any(),
                                'match_local_pref_eq': Any(),
                                'match_route_type': Any(),
                                'match_community_list': Any(),
                                'match_ext_community_list': Any(),
                                'match_ext_community_list_type': Any(),
                                'match_as_path_list': Any(),
                                'match_as_path_length': Any(),
                                'match_as_path_length_oper': Any(),
            
                                'match_evel_eq': Any(),
            
                                'match_area_eq': Any(),
            
                                'match_interface': Any(),
                                'match_prefix_list': Any(),
                                'match_prefix_list_v6': Any(),
                                'match_tag_list': Any(),
                            },
                            'actions': {
            
                                'set_route_origin': Any(),
                                'set_local_pref': Any(),
                                'set_next_hop': Any(),
                                'set_next_hop_v6': Any(),
                                'set_next_hop_self': Any(),
                                'set_med': Any(),
                                'set_as_path_prepend': Any(),
                                'set_as_path_prepend_repeat_n': Any(),
                                'set_community': Any(),
                                'set_community_no_export': Any(),
                                'set_community_no_advertise': Any(),
                                'set_community_additive': Any(),
                                'set_community_delete': Any(),
                                'set_ext_community_rt': Any(),
                                'set_ext_community_rt_additive': Any(),
                                'set_ext_community_soo': Any(),
                                'set_ext_community_vpn': Any(),
                                'set_ext_community_delete': Any(),
                                'set_ext_community_delete_type': Any(),
            
                                'set_level': Any(),
                                'set_metric_type': Any(),
                                'set_metric': Any(),
            
                                'set_ospf_metric_type': Any(),
                                'set_ospf_metric': Any(),
            
                                'route_disposition': Any(),
                                'set_tag': Any(),
                                'set_weight': Any(),
                                'actions': Any(),
                            },
                        },
                    },
                },
            },
        },

        'routing': {
            'info': {
                'ipv6_unicast_routing_enabled': Any(),
                'ip_routing_enabled': Any(),
                'vrf': {
                    Any(): {
                        'address_family': {
                            Any(): {
                                'routes': {
                                    Any(): {
                                        'route': Any(),
                                        'active': Any(),
                                        'route_preference': Any(),
                                        'metric': Any(),
                                        'source_protocol': Any(),
                                        'source_protocol_codes': Any(),
                                        'last_updated': Any(),
                                        'next_hop': {
                                            'outgoing_interface': {
                                                Any(): {
                                                    'outgoing_interface': Any(),
                                                },
                                            },
                                            'next_hop_list': {
                                                Any(): {
                                                    'index': Any(),
                                                    'next_hop': Any(),
                                                    'outgoing_interface': Any(),
                                                    'updated': Any(),
                                                },
                                            },
                                            'special_nex_hop': {
                                                Any(): {
                                                    'special_next_hop': Any(),
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'segment_routing': {
        },

        'static_routing': {
            'info': {
                'vrf': {
                    Any(): {
                        'address_family': {
                            Any(): {
                                'routes': {
                                    Any(): {
                                        'route': Any(),
                                        'next_hop': {
                                            'outgoing_interface': {
                                                Any(): {
                                                    'outgoing_interface': Any(),
                                                    'active': Any(),
                                                    'preference': Any(),
                                                    'tag': Any(),
                                                    'track': Any(),
                                                    'next_hop_vrf': Any(),
                                                },
                                            },
                                            'next_hop_list': {
                                                Any(): {
                                                    'index': Any(),
                                                    'active': Any(),
                                                    'next_hop': Any(),
                                                    'outgoing_interface': Any(),
                                                    'preference': Any(),
                                                    'tag': Any(),
                                                    'track': Any(),
                                                    'next_hop_vrf': Any(),
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'stp': {
            'info': {
                'global': {
                    'bridge_assurance': Any(),
                    'etherchannel_misconfig_guard': Any(),
                    'bpduguard_timeout_recovery': Any(),
                    'loop_guard': Any(),
                    'bpdu_guard': Any(),
                    'bpdu_filter': Any(),
                },
                'mstp': {
                    Any(): {
                        'domain': Any(),
                        'name': Any(),
                        'revision': Any(),
                        'max_hop': Any(),
                        'hello_time': Any(),
                        'max_age': Any(),
                        'forwarding_delay': Any(),
                        'hold_count': Any(),
                        'mst_instances': {
                            Any(): {
                                'mst_id': Any(),
                                'vlan': Any(),
                                'bridge_priority': Any(),
                                'bridge_address': Any(),
                                'designated_root_priority': Any(),
                                'designated_root_address': Any(),
                                'root_port': Any(),
                                'root_cost': Any(),
                                'hold_time': Any(),
                                'topology_changes': Any(),
                                'time_since_topology_change': Any(),
                                'interfaces': {
                                    Any(): {
                                        'name': Any(),
                                        'cost': Any(),
                                        'port_priority': Any(),
                                        'port_num': Any(),
                                        'role': Any(),
                                        'port_state': Any(),
                                        'designated_root_priority': Any(),
                                        'designated_root_address': Any(),
                                        'designated_cost': Any(),
                                        'designated_bridge_priority': Any(),
                                        'designated_bridge_address': Any(),
                                        'designated_port_priority': Any(),
                                        'designated_port_num': Any(),
                                        'forward_transitions': Any(),
                                        'counters': {
                                            'bpdu_sent': Any(),
                                            'bpdu_received': Any(),
                                        },
                                    },
                                },
                            },
                        },
                        'interfaces': {
                            Any(): {
                                'name': Any(),
                                'edge_port': Any(),
                                'link_type': Any(),
                                'guard': Any(),
                                'bpdu_guard': Any(),
                                'bpdu_filter': Any(),
                            },
                        },
                    },
                },
                'mstag': {
                    Any(): {
                        'domain': Any(),
                        'interfaces': {
                            Any(): {
                                'interface': Any(),
                                'name': Any(),
                                'revision': Any(),
                                'bridge_id': Any(),
                                'preempt_delay': Any(),
                                'preempt_delay_state': Any(),
                                'max_age': Any(),
                                'provider_bridge': Any(),
                                'port_id': Any(),
                                'external_cost': Any(),
                                'hello_time': Any(),
                                'active': Any(),
                                'counters': {
                                    'bpdu_sent': Any(),
                                },
                            },
                            'instances': {
                                Any(): {
                                    'instance': Any(),
                                    'root_id': Any(),
                                    'vlans': Any(),
                                    'priority': Any(),
                                    'root_priority': Any(),
                                    'port_priority': Any(),
                                    'cost': Any(),
                                    'counters': {
                                        'topology_changes': Any(),
                                    },
                                },
                            },
                        },
                    },
                },
                'pvst': {
                    Any(): {
                        'pvst_id': Any(),
                        'max_age': Any(),
                        'hold_count': Any(),
                        'forwarding_delay': Any(),
                        'hello_time': Any(),
                        'vlans': {
                            Any(): {
                                'vlan_id': Any(),
                                'hello_time': Any(),
                                'max_age': Any(),
                                'forwarding_delay': Any(),
                                'bridge_priority': Any(),
                                'configured_bridge_priority': Any(),
                                'sys_id_ext': Any(),
                                'bridge_address': Any(),
                                'designated_root_priority': Any(),
                                'designated_root_address': Any(),
                                'root_port': Any(),
                                'root_cost': Any(),
                                'hold_time': Any(),
                                'topology_changes': Any(),
                                'time_since_topology_change': Any(),
                                'interface': {
                                    Any(): {
                                        'name': Any(),
                                        'cost': Any(),
                                        'port_priority': Any(),
                                        'port_num': Any(),
                                        'role': Any(),
                                        'port_state': Any(),
                                        'designated_root_priority': Any(),
                                        'designated_root_address': Any(),
                                        'designated_cost': Any(),
                                        'designated_bridge_priority': Any(),
                                        'designated_bridge_address': Any(),
                                        'designated_port_priority': Any(),
                                        'designated_port_num': Any(),
                                        'forward_transitions': Any(),
                                        'counters': {
                                            'bpdu_sent': Any(),
                                            'bpdu_received': Any(),
                                        },
                                    },
                                },
                            },            
                        },
                        'interfaces': {
                            Any(): {
                                'name': Any(),
                                'edge_port': Any(),
                                'link_type': Any(),
                                'guard': Any(),
                                'bpdu_guard': Any(),
                                'bpdu_filter': Any(),
                                'hello_time': Any(),
                            },
                        },
                    },
                },
                'rapid_pvst': {
                    Any(): {
                        'pvst_id': Any(),
                        'max_age': Any(),
                        'hold_count': Any(),
                        'forwarding_delay': Any(),
                        'hello_time': Any(),
                        'vlans': {
                            Any(): {
                                'vlan_id': Any(),
                                'hello_time': Any(),
                                'max_age': Any(),
                                'forwarding_delay': Any(),
                                'bridge_priority': Any(),
                                'configured_bridge_priority': Any(),
                                'sys_id_ext': Any(),
                                'bridge_address': Any(),
                                'designated_root_priority': Any(),
                                'designated_root_address': Any(),
                                'root_port': Any(),
                                'root_cost': Any(),
                                'hold_time': Any(),
                                'topology_changes': Any(),
                                'time_since_topology_change': Any(),
                                'interface': {
                                    Any(): {
                                        'name': Any(),
                                        'cost': Any(),
                                        'port_priority': Any(),
                                        'port_num': Any(),
                                        'role': Any(),
                                        'port_state': Any(),
                                        'designated_root_priority': Any(),
                                        'designated_root_address': Any(),
                                        'designated_cost': Any(),
                                        'designated_bridge_priority': Any(),
                                        'designated_bridge_address': Any(),
                                        'designated_port_priority': Any(),
                                        'designated_port_num': Any(),
                                        'forward_transitions': Any(),
                                        'counters': {
                                            'bpdu_sent': Any(),
                                            'bpdu_received': Any(),
                                        },
                                    },
                                },
                            },            
                        },
                        'interfaces': {
                            Any(): {
                                'name': Any(),
                                'edge_port': Any(),
                                'link_type': Any(),
                                'guard': Any(),
                                'bpdu_guard': Any(),
                                'bpdu_filter': Any(),
                                'hello_time': Any(),
                            },
                        },
                    },
                },
                'pvrstag': {
                    Any(): {
                        'domain': Any(),
                        'interfaces': {
                            Any(): {
                                'interface': Any(),
                                'vlans': {
                                    Any(): {
                                        'root_priority': Any(),
                                        'root_id': Any(),
                                        'root_cost': Any(),
                                        'priority': Any(),
                                        'bridge_id': Any(),
                                        'port_priority': Any(),
                                        'max_age': Any(),
                                        'hello_time': Any(),
                                        'preempt_delay': Any(),
                                        'preempt_delay_state': Any(),
                                        'sub_interface': Any(),
                                        'sub_interface_state': Any(),
                                        'port_id': Any(),
                                        'active': Any(),
                                        'counters': {
                                            'bpdu_sent': Any(),
                                            'topology_changes': Any(),
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
                'pvstag': {
                    Any(): {
                        'domain': Any(),
                        'interfaces': {
                            Any(): {
                                'interface': Any(),
                                'vlans': {
                                    Any(): {
                                        'root_priority': Any(),
                                        'root_id': Any(),
                                        'root_cost': Any(),
                                        'priority': Any(),
                                        'bridge_id': Any(),
                                        'port_priority': Any(),
                                        'max_age': Any(),
                                        'hello_time': Any(),
                                        'preempt_delay': Any(),
                                        'preempt_delay_state': Any(),
                                        'sub_interface': Any(),
                                        'sub_interface_state': Any(),
                                        'port_id': Any(),
                                        'active': Any(),
                                        'counters': {
                                            'bpdu_sent': Any(),
                                            'topology_changes': Any(),
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'vlan': {
            'info': {
                'vlans': {
                    'interface_vlan_enabled': Any(),
                    'vn_segment_vlan_based_enabled': Any(),
                    Any(): {
                        'vlan_id': Any(),
                        'shutdown': Any(),
                        'name': Any(),
                        'state': Any(),
                        'interfaces': Any(),
                        'vn_segment_id': Any(),
                        'mode': Any(),
                    },
                    'configuration': {
                        Any(): {
                            'ip_igmp_snooping': Any(),
                        },
                    },
                },
            },
        },

        'vrf': {
            'info': {
                'vrfs': {
                    Any(): {
                        'route_distinguisher': Any(),
                        'shutdown': Any(),
                        'address_family': {
                            Any(): {
                                'route-targets': {
                                    Any(): {
                                        'route-target': Any(),
                                        'rt-type': Any(),
                                    },
                                },
                                'import-from-global': {
                                    'import_from_global_map': Any(),
                                },
                                'export-to-global': {
                                    'export_to_global_map': Any(),
                                },
                                'routing_table_limit': {
                                    'routing_table_limit_number': Any(),
                                    'routing-table_limit_action': {
                                        'enable_alert_percent': {
                                            'alert_percent_value': Any(),
                                        },
                                        'enable_alert_limit_number': {
                                            'alert_limit_number': Any(),
                                        },
                                        'enable_simple_alert': {
                                            'simple_alert': Any(),
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },

        'vxlan': {
            'nve': {
                'enabled': Any(),
                'enabled_nv_overlay': Any(),
                'enabled_vn_segment_vlan_based': Any(),
                'enabled_nv_overlay_evpn': Any(),
                'fabric_fwd_anycast_gw_mac': Any(),
                'vni': {
                    'summary': {
                        'cp_vni_count': Any(),
                        'cp_vni_up': Any(),
                        'cp_vni_down': Any(),
                        'dp_vni_count': Any(),
                        'dp_vni_up': Any(),
                        'dp_vni_down': Any(),
                    },
                },
                Any(): {
                    'nve_name': Any(),
                    'if_state': Any(),
                    'encap_type': Any(),
                    'vpc_capability': Any(),
                    'local_rmac': Any(),
                    'host_reach_mode': Any(),
                    'source_if': Any(),
                    'primary_ip': Any(),
                    'secondary_ip': Any(),
                    'src_if_state': Any(),
                    'ir_cap_mode': Any(),
                    'adv_vmac': Any(),
                    'nve_flags': Any(),
                    'nve_if_handle': Any(),
                    'src_if_holddown_tm': Any(),
                    'src_if_holdup_tm': Any(),
                    'src_if_holddown_left': Any(),
                    'multisite_convergence_time': Any(),
                    'multisite_convergence_time_left': Any(),
                    'vpc_compat_check': Any(),
                    'vip_rmac': Any(),
                    'vip_rmac_ro': Any(),
                    'sm_state': Any(),
                    'peer_forwarding_mode': Any(),
                    'dwn_strm_vni_cfg_mode': Any(),
                    'src_intf_last_reinit_notify_type': Any(),
                    'mcast_src_intf_last_reinit_notify_type': Any(),
                    'multi_src_intf_last_reinit_notify_type': Any(),
                    'multisite_bgw_if': Any(),
                    'multisite_bgw_if_ip': Any(),
                    'multisite_bgw_if_admin_state': Any(),
                    'multisite_bgw_if_oper_state': Any(),
                    'multisite_bgw_if_oper_state_down_reason': Any(),
                    'peer_ip': {
                        Any(): {
                            'peer_state': Any(),
                            'learn_type': Any(),
                            'uptime': Any(),
                            'router_mac': Any(),
                        },
                    },
                    'ethernet_segment': {
                        'esi': {
                            Any(): {
                                'esi': Any(),
                                'if_name': Any(),
                                'es_state': Any(),
                                'po_state': Any(),
                                'nve_if_name': Any(),
                                'nve_state': Any(),
                                'host_reach_mode': Any(),
                                'active_vlans': Any(),
                                'df_vlans': Any(),
                                'active_vnis': Any(),
                                'cc_failed_vlans': Any(),
                                'cc_timer_left': Any(),
                                'num_es_mem': Any(),
                                'local_ordinal': Any(),
                                'df_timer_st': Any(),
                                'config_status': Any(),
                                'df_list': Any(),
                                'es_rt_added': Any(),
                                'ead_rt_added': Any(),
                                'ead_evi_rt_timer_age': Any(),
                            },
                        },
                    },
                    'vni': {
                        Any(): {
                            'vni': Any(),
                            'mcast': Any(),
                            'vni_state': Any(),
                            'mode': Any(),
                            'type': Any(),
                            'flags': Any(),
                            'repl_ip': {
                                Any(): {
                                    'repl_ip': Any(),
                                    'source': Any(),
                                    'up_time': Any(),
                                },
                            },
                        },
                    },
                },
                'multisite': {
                    'dci_links': {
                        Any(): {
                            'if_name': Any(),
                            'if_state': Any(),
                        },
                    },
                    'fabric_links': {
                        Any(): {
                            'if_name': Any(),
                            'if_state': Any(),
                        },
                    },
                },
            },
            'l2route': {
                'evpn': {
                    'ethernet_segment': {
                        Any(): {
                            'ethernet_segment': Any(),
                            'originating_rtr': Any(),
                            'prod_name': Any(),
                            'int_ifhdl': Any(),
                            'client_nfn': Any(),
                        },
                    },
                },
                'topology': {
                    'topo_id': {
                        Any(): {
                            'num_of_peer_id': Any(),
                            'peer_id': {
                                Any(): {
                                    'topo_id': Any(),
                                    'peer_id': Any(),
                                    'flood_list': Any(),
                                    'is_service_node': Any(),
                                },
                            },
                            'topo_name': {
                                Any(): {
                                    'topo_name': Any(),
                                    'topo_type': Any(),
                                    'vni': Any(),
                                    'encap_type': Any(),
                                    'iod': Any(),
                                    'if_hdl': Any(),
                                    'vtep_ip': Any(),
                                    'emulated_ip': Any(),
                                    'emulated_ro_ip': Any(),
                                    'tx_id': Any(),
                                    'rcvd_flag': Any(),
                                    'rmac': Any(),
                                    'vrf_id': Any(),
                                    'vmac': Any(),
                                    'flags': Any(),
                                    'sub_flags': Any(),
                                    'prev_flags': Any(),
                                },
                            },
                            'mac': {
                                Any(): {
                                    'mac_addr': Any(),
                                    'prod_type': Any(),
                                    'flags': Any(),
                                    'seq_num': Any(),
                                    'next_hop1': Any(),
                                    'rte_res': Any(),
                                    'fwd_state': Any(),
                                    'peer_id': Any(),
                                    'sent_to': Any(),
                                    'soo': Any(),
                                },
                            },
                            'mac_ip': {
                                Any(): {
                                    'mac_addr': Any(),
                                    'mac_ip_prod_type': Any(),
                                    'mac_ip_flags': Any(),
                                    'seq_num': Any(),
                                    'next_hop1': Any(),
                                    'host_ip': Any(),
                                    'sent_to': Any(),
                                    'soo': Any(),
                                    'l3_info': Any(),
                                },
                            },
                        },
                    },
                },
                'summary': {
                    'total_memory': Any(),
                    'numof_converged_tables': Any(),
                    'table_name': {
                        Any(): {
                            'producer_name': {
                                Any(): {
                                    'producer_name': Any(),
                                    'id': Any(),
                                    'objects': Any(),
                                    'memory': Any(),
                                },
                                'total_obj': Any(),
                                'total_mem': Any(),
                            },
                        },
                    },
                },
            },
            'bgp_l2vpn_evpn': {
                'instance': {
                    Any(): {
                        'vrf': {
                            Any(): {
                                'vrf_name_out': Any(),
                                'vrf_router_id': Any(),
                                'vrf_local_as': Any(),
                                'address_family': {
                                    Any(): {
                                        'tableversion': Any(),
                                        'configuredpeers': Any(),
                                        'capablepeers': Any(),
                                        'totalnetworks': Any(),
                                        'totalpaths': Any(),
                                        'memoryused': Any(),
                                        'numberattrs': Any(),
                                        'bytesattrs': Any(),
                                        'numberpaths': Any(),
                                        'bytespaths': Any(),
                                        'numbercommunities': Any(),
                                        'bytescommunities': Any(),
                                        'numberclusterlist': Any(),
                                        'bytesclusterlist': Any(),
                                        'dampening': Any(),
                                        'neighbor': {
                                            Any(): {
                                                'neighbor': Any(),
                                                'version': Any(),
                                                'msgrecvd': Any(),
                                                'msgsent': Any(),
                                                'neighbortableversion': Any(),
                                                'inq': Any(),
                                                'outq': Any(),
                                                'remoteas': Any(),
                                                'elapsedtime': Any(),
                                                'state': Any(),
                                                'prefixreceived': Any(),
                                                'localas': Any(),
                                                'link': Any(),
                                                'index': Any(),
                                                'remote_id': Any(),
                                                'up': Any(),
                                                'connectedif': Any(),
                                                'bfd': Any(),
                                                'ttlsecurity': Any(),
                                                'password': Any(),
                                                'passiveonly': Any(),
                                                'localas_inactive': Any(),
                                                'remote_privateas': Any(),
                                                'lastread': Any(),
                                                'holdtime': Any(),
                                                'keepalivetime': Any(),
                                                'lastwrite': Any(),
                                                'keepalive': Any(),
                                                'notificationsrcvd': Any(),
                                                'recvbufbytes': Any(),
                                                'notificationsent': Any(),
                                                'sentbytesoutstanding': Any(),
                                                'connsestablished': Any(),
                                                'connsdropped': Any(),
                                                'resettime': Any(),
                                                'resetreason': Any(),
                                                'peerresettime': Any(),
                                                'peerresetreason': Any(),
                                                'capsnegotiated': Any(),
                                                'capmpadvertised': Any(),
                                                'caprefreshadvertised': Any(),
                                                'capgrdynamicadvertised': Any(),
                                                'capmprecvd': Any(),
                                                'caprefreshrecvd': Any(),
                                                'capgrdynamicrecvd': Any(),
                                                'capolddynamicadvertised': Any(),
                                                'capolddynamicrecvd': Any(),
                                                'caprradvertised': Any(),
                                                'caprrrecvd': Any(),
                                                'capoldrradvertised': Any(),
                                                'capoldrrrecvd': Any(),
                                                'capas4advertised': Any(),
                                                'capas4recvd': Any(),
                                                'af': {
                                                    Any(): {
                                                        'af_advertised': Any(),
                                                        'af_recvd': Any(),
                                                        'af_name': Any(),
                                                    },
                                                },
                                                'capgradvertised': Any(),
                                                'capgrrecvd': Any(),
                                                'graf': {
                                                    Any(): {
                                                        'gr_af_name': Any(),
                                                        'gr_adv': Any(),
                                                        'gr_recv': Any(),
                                                        'gr_fwd': Any(),
                                                    },
                                                },
                                                'grrestarttime': Any(),
                                                'grstaletiem': Any(),
                                                'grrecvdrestarttime': Any(),
                                                'capextendednhadvertised': Any(),
                                                'capextendednhrecvd': Any(),
                                                'capextendednhaf': {
                                                    Any(): {
                                                        'capextendednh_af_name': Any(),
                                                    },
                                                },
                                                'epe': Any(),
                                                'firstkeepalive': Any(),
                                                'openssent': Any(),
                                                'opensrecvd': Any(),
                                                'updatessent': Any(),
                                                'updatesrecvd': Any(),
                                                'keepalivesent': Any(),
                                                'keepaliverecvd': Any(),
                                                'rtrefreshsent': Any(),
                                                'rtrefreshrecvd': Any(),
                                                'capabilitiessent': Any(),
                                                'capabilitiesrecvd': Any(),
                                                'bytessent': Any(),
                                                'bytesrecvd': Any(),
                                                'peraf': {
                                                    Any(): {
                                                        'per_af_name': Any(),
                                                        'tableversion': Any(),
                                                        'neighbortableversion': Any(),
                                                        'pfxrecvd': Any(),
                                                        'pfxbytes': Any(),
                                                        'insoftreconfigallowed': Any(),
                                                        'sendcommunity': Any(),
                                                        'sendextcommunity': Any(),
                                                        'asoverride': Any(),
                                                        'peerascheckdisabled': Any(),
                                                        'rrconfigured': Any(),
                                                    },
                                                },
                                                'localaddr': Any(),
                                                'localport': Any(),
                                                'remoteaddr': Any(),
                                                'remoteport': Any(),
                                                'fd': Any(),
                                            },
                                        },
                                        'rd': {
                                            Any(): {
                                                'rd': Any(),
                                                'rd_vrf': Any(),
                                                'rd_vniid': Any(),
                                                'prefix': {
                                                    Any(): {
                                                        'nonipprefix': Any(),
                                                        'prefixversion': Any(),
                                                        'totalpaths': Any(),
                                                        'bestpathnr': Any(),
                                                        'on_newlist': Any(),
                                                        'on_xmitlist': Any(),
                                                        'suppressed': Any(),
                                                        'needsresync': Any(),
                                                        'locked': Any(),
                                                        'mpath': Any(),
                                                        'path': {
                                                            Any(): {
                                                                'pathnr': Any(),
                                                                'policyincomplete': Any(),
                                                                'pathvalid': Any(),
                                                                'pathbest': Any(),
                                                                'pathdeleted': Any(),
                                                                'pathstaled': Any(),
                                                                'pathhistory': Any(),
                                                                'pathovermaxaslimit': Any(),
                                                                'pathmultipath': Any(),
                                                                'pathnolabeledrnh': Any(),
                                                                'importdestcount': Any(),
                                                                'ipnexthop': Any(),
                                                                'nexthopmetric': Any(),
                                                                'neighbor': Any(),
                                                                'neighborid': Any(),
                                                                'origin': Any(),
                                                                'localpref': Any(),
                                                                'weight': Any(),
                                                                'inlabel': Any(),
                                                                'extcommunity': Any(),
                                                                'advertisedto': Any(),
                                                                'originatorid': Any(),
                                                                'clusterlist': Any(),
                                                                'pmsi_tunnel_attribute': {
                                                                    'label': Any(),
                                                                    'flags': Any(),
                                                                    'tunnel_id': Any(),
                                                                    'tunnel_type': Any(),
                                                                },
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            'fabric': {
                'enabled_ngmvpn': Any(),
                'multicast': {
                    'globals': {
                        'pruning': Any(),
                        'switch_role': Any(),
                        'fabric_control_seg': Any(),
                        'peer_fabric_ctrl_addr': Any(),
                        'advertise_vpc_rpf_routes': Any(),
                        'created_vni_list': Any(),
                        'fwd_encap': Any(),
                        'overlay_distributed_dr': Any(),
                        'overlay_spt_only': Any(),
                    },
                    'vrf': {
                        Any(): {
                            'vnid': Any(),
                            'address_family': {
                                Any(): {
                                    'sa_ad_routes': {
                                        'gaddr': {
                                            Any(): {
                                                'grp_len': Any(),
                                                'saddr': {
                                                    '100.101.1.3/32': {
                                                        'src_len': Any(),
                                                        'uptime': Any(),
                                                        'interested_fabric_nodes': {
                                                            Any(): {
                                                                'uptime': Any(),
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                    'l2_mroute': {
                        'vni': {
                            Any(): {
                                'vnid': Any(),
                                'fabric_l2_mroutes': {
                                    'gaddr': {
                                        Any(): {
                                            'saddr': {
                                                Any(): {
                                                    'interested_fabric_nodes': {
                                                        Any(): {
                                                            'node': Any(),
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            'forwarding': {
                'distribution': {
                    'multicast': {
                        'route': {
                            'vrf': {
                                Any(): {
                                    'address_family': {
                                        Any(): {
                                            'num_groups': Any(),
                                            'gaddr': {
                                                Any(): {
                                                    'grp_len': Any(),
                                                    'saddr': {
                                                        Any(): {
                                                            'rpf_ifname': Any(),
                                                            'src_len': Any(),
                                                            'flags': Any(),
                                                            'rcv_packets': Any(),
                                                            'rcv_bytes': Any(),
                                                            'num_of_oifs': Any(),
                                                            'oifs': {
                                                                'oif_index': Any(),
                                                                Any(): {
                                                                    'encap': Any(),
                                                                    'mem_l2_ports': Any(),
                                                                    'l2_oiflist_index': Any(),
                                                                },
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
            'bgp_mvpn': {
                'instance': {
                    Any(): {
                        'vrf': {
                            Any(): {
                                'vrf_name_out': Any(),
                                'address_family': {
                                    Any(): {
                                        'af_name': Any(),
                                        'table_version': Any(),
                                        'router_id': Any(),
                                        'rd': {
                                            Any(): {
                                                'rd_val': Any(),
                                                'rd_vrf': Any(),
                                                'prefix': {
                                                    Any(): {
                                                        'nonipprefix': Any(),
                                                        'prefixversion': Any(),
                                                        'totalpaths': Any(),
                                                        'bestpathnr': Any(),
                                                        'on_newlist': Any(),
                                                        'on_xmitlist': Any(),
                                                        'suppressed': Any(),
                                                        'needsresync': Any(),
                                                        'locked': Any(),
                                                        'path': {
                                                            Any(): {
                                                                'pathnr': Any(),
                                                                'policyincomplete': Any(),
                                                                'pathvalid': Any(),
                                                                'pathbest': Any(),
                                                                'pathdeleted': Any(),
                                                                'pathstaled': Any(),
                                                                'pathhistory': Any(),
                                                                'pathovermaxaslimit': Any(),
                                                                'pathmultipath': Any(),
                                                                'pathnolabeledrnh': Any(),
                                                                'status': Any(),
                                                                'best': Any(),
                                                                'type': Any(),
                                                                'statuscode': Any(),
                                                                'bestcode': Any(),
                                                                'typecode': Any(),
                                                                'ipnexthop': Any(),
                                                                'weight': Any(),
                                                                'origin': Any(),
                                                                'localpref': Any(),
                                                                'nexthopmetric': Any(),
                                                                'neighbor': Any(),
                                                                'neighborid': Any(),
                                                                'extcommunity': Any(),
                                                                'advertisedto': Any(),
                                                            },
                                                        },
                                                    },
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
            },
        },
    }