import csv

dat_header = ['# Entry', 'prescale', 'multiplicity', 'mul_pre_SD', 
              'events_being_read', 'hardest_pT', 'jec', 'jet_quality', 
              'hardest_eta', 'crosssection', 'trigger_fired', 
              'hardest_phi', 'hardest_area', 'zg_05', 'mu_05', 'rg_05', 
              'e1_05', 'e2_05', 'e05_05', 'zg_10', 'mu_10', 
              'rg_10', 'e1_10', 'e2_10', 'e05_10', 'zg_20', 
              'mu_20', 'rg_20', 'e1_20', 'e2_20', 'e05_20', 
              'pT_after_SD', 'mul_pre_SD', 'mul_post_SD', 
              'mul_filtered_SD', 'mass_pre_SD', 'mass_post_SD',
              'pT_D_pre_SD', 'pT_D_post_SD', 'LHA_pre_SD', 
              'LHA_post_SD', 'width_pre_SD', 'width_post_SD', 
              'thrust_pre_SD', 'thrust_post_SD', 'track_zg_05', 
              'track_mu_05', 'track_rg_05', 'track_e1_05', 
              'track_e2_05', 'track_e05_05', 'track_zg_10', 
              'track_mu_10', 'track_rg_10', 'track_e1_10', 'track_e2_10',
              'track_e05_10', 'track_zg_20', 'track_mu_20', 'track_rg_20',
              'track_e1_20', 'track_e2_20', 'track_e05_20', 
              'track_mul_pre_SD', 'track_mul_post_SD', 'track_mass_pre_SD', 
              'track_mass_post_SD', 'track_pT_D_pre_SD', 'track_pT_D_post_SD',
              'track_LHA_pre_SD', 'track_LHA_post_SD', 'track_width_pre_SD',
              'track_width_post_SD', 'track_thrust_pre_SD',
              'track_thrust_post_SD']

def write_dat_header(writer):
    writer.writerow(dat_header)

def write_dat_event(writer, event):
    dat_row = ['Entry']
    for col in dat_header:
        if col == 'prescale':
            dat_row.append(str(event.prescale()))
        elif col == 'mul_pre_SD':
            dat_row.append(str(event.mul_pre_SD()))
        elif col == 'hardest_pT':
            dat_row.append(str(event.hardest_pT()))
        elif col == 'hardest_eta':
            dat_row.append(str(event.hardest_eta()))
        elif col == 'hardest_phi':
            dat_row.append(str(event.hardest_phi()))
        elif col == 'hardest_area':
            dat_row.append(str(event.hardest_area()))
        elif col == 'jec':
            dat_row.append(str(event.jec()))
        elif col == 'jet_quality':
            dat_row.append(str(event.jet_quality()))
        elif col == 'trigger_fired':
            dat_row.append(str(event.trigger_fired()))
        else:
            dat_row.append('nan')

    writer.writerow(dat_row)