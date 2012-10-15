

import numpy as np
from paper_plot import tmp_plot

def load_scat_mat(name, st, p):
    # reshape matrices to be consistent with pcpv.exe output
    format_title = '%04d' % st
    format_p     = '%04d' % p

    file_name = "st%(st)s_wl%(wl)s_%(mat_name)s.txt" % {
        'st' : format_title, 'wl' : format_p, 'mat_name' : name }
    data   = np.loadtxt(file_name)
    num_1  = max(data[:,0])
    num_2  = max(data[:,1])
    matrix = np.mat(data[:,2] + data[:,3]*(0+1j))
    matrix = np.reshape(matrix, (num_2, num_1))
    return matrix

def load_k_perp(name, st, p):
    # reshape matrices to be consistent with pcpv.exe output
    format_title = '%04d' % st
    format_p     = '%04d' % p

    file_name = "st%(st)s_wl%(wl)s_%(mat_name)s.txt" % {
        'st' : format_title, 'wl' : format_p, 'mat_name' : name }
    data   = np.loadtxt(file_name)
    return data


def rmat_through_air(top_layer, bot_layer, wl):
    # P -> I for infinitesimal air layer
    r10 = load_scat_mat('R21', top_layer.label_nu, wl).T
    t01 = load_scat_mat('T12', top_layer.label_nu, wl).T
    r01 = load_scat_mat('R12', top_layer.label_nu, wl).T
    r02 = load_scat_mat('R12', bot_layer.label_nu, wl).T
    t10 = load_scat_mat('T21', top_layer.label_nu, wl).T
    I_mat    = np.matrix(np.eye(len(r01)),dtype='D')
    to_invert = (I_mat - r01*r02)
    inverted  = np.linalg.solve(to_invert,t10)
    rmat = r10 + t01*r02*inverted
    # inv_term = (I_mat - r01*r02).I
    # rmat = r10 + t01*r02*inv_term*t10
    return rmat#.T

def tmat_through_air(top_layer, bot_layer, wl):
    # P -> I for infinitesimal air layer
    t02 = load_scat_mat('T12', bot_layer.label_nu, wl).T
    r01 = load_scat_mat('R12', top_layer.label_nu, wl).T
    r02 = load_scat_mat('R12', bot_layer.label_nu, wl).T
    t10 = load_scat_mat('T21', top_layer.label_nu, wl).T
    I_mat    = np.matrix(np.eye(len(r01)),dtype='D')
    to_invert = (I_mat - r01*r02)
    inverted  = np.linalg.solve(to_invert,t10)
    tmat = t02*inverted
    # inv_term = (I_mat - r01*r02).I
    # tmat = t02*inv_term*t10
    return tmat#.T


def save_TR_mats(matrix, name, p):
            # reshape matrices to be consistent with pcpv.exe output
            format_p     = '%04d' % p

            file_name = "wl%(wl)s_%(mat_name)s.txt" % {
                'wl' : format_p, 'mat_name' : name }
            num_pw = len(matrix)
            with file(file_name, 'w') as outfile:
                for k in range(num_pw):
                    for i in range(num_pw):
                        data = [i+1,  k+1, np.real(matrix[i,k]), np.imag(matrix[i,k]),
                            np.abs(matrix[i,k])**2]
                        data = np.reshape(data, (1,5))
                        np.savetxt(outfile, data, fmt=['%4i','%4i','%25.17G','%25.17G','%25.17G'], delimiter='')



def net_scat_mats(solar_cell, wavelengths):
    Transmittance = []
    Reflectance   = []
    Absorptance   = []
    T_save = []
    R_save = []
    A_save = []
    for p in range(len(wavelengths)):
        p += 1

        # calculate list of scattering matrices of interfaces without air slices\
        # notice counting upwards from substrate!
        # ie r12s[0] = refelction from layer 0 off layer 1
        r12s = []
        r21s = []
        t12s = []
        t21s = []
        for st1, st2 in zip(solar_cell[:-1], solar_cell[1:]):
            r12s.append(rmat_through_air(st1, st2, p))
            r21s.append(rmat_through_air(st2, st1, p))
            t12s.append(tmat_through_air(st1, st2, p))
            t21s.append(t12s[-1].T)
            # t21s.append(tmat_through_air(st2, st1, p))

        # iterate through solar cell to find total Tnet, Rnet matrices
        P     = []
        rnet  = []
        tnet  = []
        delta = 
        rnet[0] = r21s[0]
        tnet[0] = t21s[0]

        for i in range(1,len(solar_cell)-1):
            P = load_scat_mat('P', solar_cell[i].label_nu, p).T
            I_mat   = np.matrix(np.eye(len(P)),dtype='D')
            to_invert = (I_mat - r12s[i]*P*rnet*P)
            inverted  = np.linalg.solve(to_invert,t21s[i])
            repeated_term = P*inverted
            tnet = tnet*repeated_term
            rnet = r21s[i] + t12s[i]*P*rnet*repeated_term
            ## k_perp for when want to calculate many thicknesses from set matrices
            # k_perp = load_k_perp('beta', solar_cell[i].label_nu, p)
            # h_normed = float(layer.height_1)/d_in_nm
            # P_array  = np.exp(1j*np.array(k_film, complex)*h_normed)
            # P_array  = np.append(P_array, P_array) # add 2nd polarisation
            # P        = np.matrix(np.diag(P_array),dtype='D')
            # save_scat_mat(P, 'P', layer.label_nu, p, matrix_size)











    #     # save_TR_mats(tnet, 'Tnet', p)
    #     # save_TR_mats(rnet, 'Rnet', p)


    #     # select elements of Tnet, Rnet matrices to calculate absorption etc.
    #     neq_PW   = solar_cell[0].nu_tot_ords
    #     select_ord_in  = solar_cell[-1].set_ord_in
    #     select_ord_out = solar_cell[0].set_ord_out

    #     inc      = solar_cell[0].zero_ord
    #     Lambda_t = 0
    #     for i in range(solar_cell[0].nu_prop_ords):
    #         #TM
    #         # Lambda_t = Lambda_t + abs(tnet[i,neq_PW+inc])**2 + abs(tnet[neq_PW+i,neq_PW+inc])**2
    #         #TE
    #         Lambda_t = Lambda_t + abs(tnet[i,inc])**2 + abs(tnet[neq_PW+i,inc])**2

    #     inc      = solar_cell[-1].zero_ord
    #     Lambda_r = 0
    #     for i in range(solar_cell[-1].nu_prop_ords):
    #         #TM
    #         # Lambda_r = Lambda_r + abs(rnet[i,neq_PW+inc])**2 + abs(rnet[neq_PW+i,neq_PW+inc])**2
    #         #TE
    #         Lambda_r = Lambda_r + abs(rnet[i,inc])**2 + abs(rnet[neq_PW+i,inc])**2

    #     absorption = 1 - Lambda_r - Lambda_t


    #     Transmittance.append(Lambda_t)
    #     Reflectance.append(Lambda_r)
    #     Absorptance.append(absorption)
    #     T_save.append((wavelengths[p-1], Lambda_t))
    #     R_save.append((wavelengths[p-1], Lambda_r))
    #     A_save.append((wavelengths[p-1], absorption))

    # np.savetxt('Transmittance.txt', T_save, fmt=['%18.10f','%25.17G'], delimiter='')
    # np.savetxt('Reflectance.txt', R_save, fmt=['%18.10f','%25.17G'], delimiter='')
    # np.savetxt('Absorptance.txt', A_save, fmt=['%18.10f','%25.17G'], delimiter='')

    # # relative_wave_nu = 120/wavelengths

    # # tmp_plot(relative_wave_nu, Reflectance, 'R_Spec')
    # # tmp_plot(relative_wave_nu, Transmittance, 'T_Spec')
    # # tmp_plot(relative_wave_nu, Absorptance, 'A_Spec')