C=======================================================================  
C UMAT for Steel Plasticity with Failure 
C J2 Flow Theory with Isotropic Hardening and Failure Criterion 
C=======================================================================  
      SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,  
     1 RPL,DDSDDT,DRPLDE,DRPLDT,  
     2 STRAN,DSTRAN,TIME,DTIME,TEMP,DTEMP,  
     3 PREDEF,DPRED,CMNAME,NDI,NSHR,NTENS,NSTATV,  
     4 PROPS,NPROPS,COORDS,DROT,PNEWDT,  
     5 CELENT,DFGRD0,DFGRD1,NOEL,NPT,LAYER,KSPT,  
     6 KSTEP,KINC)  
C  
      INCLUDE 'ABA_PARAM.INC'  
C  
      CHARACTER*80 CMNAME  
      DIMENSION STRESS(NTENS),STATEV(NSTATV),  
     1 DDSDDE(NTENS,NTENS),DDSDDT(NTENS),DRPLDE(NTENS),  
     2 STRAN(NTENS),DSTRAN(NTENS),TIME(2),PREDEF(1),DPRED(1),  
     3 COORDS(3),DROT(3,3),DFGRD0(3,3),DFGRD1(3,3)  
C  
C-----------------------------------------------------------------------  
C     MATERIAL PARAMETERS  
C-----------------------------------------------------------------------  
C     PROPS(1) - E (Young's modulus)  
C     PROPS(2) - NU (Poisson's ratio)  
C     PROPS(3) - SIGMA_Y (Initial yield stress)  
C     PROPS(4) - K (Hardening coefficient)  
C     PROPS(5) - n (Hardening exponent)  
C     PROPS(6) - EPS_FAIL (Failure strain)  
C-----------------------------------------------------------------------  
C  
C-----------------------------------------------------------------------  
C     STATE VARIABLES  
C-----------------------------------------------------------------------  
C     STATEV(1) - EQPLAS (Equivalent plastic strain)  
C     STATEV(2) - FAILURE_FLAG (1.0 = failed, 0.0 = intact)  
C-----------------------------------------------------------------------  
C  
      REAL*8 E, NU, SIGMA_Y, K, n, EPS_FAIL  
      REAL*8 G, KMOD, LAM  
      REAL*8 EQPLAS, FAILURE_FLAG  
      REAL*8 STRESS_DEV(6), P_TRIAL, TRACE  
      REAL*8 SMIS_TRIAL, YIELD_STRESS, HARD_MOD  
      REAL*8 PHI, DEQPL, DGAMMA, FACTOR, ONEMFAC  
      REAL*8 TERM1, TERM2  
      INTEGER I, J  
      PARAMETER(TOLER=1.0D-10, SQRT_2_3=0.8164965809D0)  
C  
C-----------------------------------------------------------------------  
C  READ MATERIAL PARAMETERS  
C-----------------------------------------------------------------------  
      E        = PROPS(1)    ! Young's modulus  
      NU       = PROPS(2)    ! Poisson's ratio  
      SIGMA_Y  = PROPS(3)    ! Initial yield stress  
      K        = PROPS(4)    ! Hardening coefficient  
      n        = PROPS(5)    ! Hardening exponent  
      EPS_FAIL = PROPS(6)    ! Failure strain  
C  
C-----------------------------------------------------------------------  
C  CALCULATE ELASTIC CONSTANTS  
C-----------------------------------------------------------------------  
      G    = E / (2.0D0*(1.0D0+NU))         ! Shear modulus  
      KMOD = E / (3.0D0*(1.0D0-2.0D0*NU))   ! Bulk modulus  
      LAM  = KMOD - 2.0D0*G/3.0D0            ! Lame constant  
C  
C-----------------------------------------------------------------------  
C  READ STATE VARIABLES  
C-----------------------------------------------------------------------  
      EQPLAS = STATEV(1)  
      FAILURE_FLAG = STATEV(2)  
C  
C-----------------------------------------------------------------------  
C  CHECK FOR FAILURE  
C-----------------------------------------------------------------------  
      IF (FAILURE_FLAG .GE. 1.0D0) THEN  
C       Material has failed - set stress to zero  
        DO I = 1, NTENS  
          STRESS(I) = 0.0D0  
        END DO  
C       Set tangent modulus to very small value  
        DO I = 1, NTENS  
          DO J = 1, NTENS  
            DDSDDE(I,J) = 1.0D0  
          END DO  
        END DO  
        GOTO 999  
      END IF  
C  
C-----------------------------------------------------------------------  
C  ELASTIC PREDICTOR: CALCULATE TRIAL STRESS  
C-----------------------------------------------------------------------  
C  Volumetric strain increment  
      TRACE = DSTRAN(1) + DSTRAN(2) + DSTRAN(3)  
      P_TRIAL = (STRESS(1)+STRESS(2)+STRESS(3))/3.0D0 + KMOD*TRACE  
C  
C  Deviatoric strain increment and trial deviatoric stress  
      DO I = 1, NDI  
        STRESS_DEV(I) = STRESS(I) - (STRESS(1)+STRESS(2)+STRESS(3))/3.0D0  
     1                + 2.0D0*G*(DSTRAN(I) - TRACE/3.0D0)  
      END DO  
      DO I = NDI+1, NTENS  
        STRESS_DEV(I) = STRESS(I) + 2.0D0*G*DSTRAN(I)  
      END DO  
C  
C-----------------------------------------------------------------------  
C  CALCULATE EQUIVALENT DEVIATORIC STRESS OF TRIAL STRESS  
C-----------------------------------------------------------------------  
      SMIS_TRIAL = SQRT(STRESS_DEV(1)**2 + STRESS_DEV(2)**2  
     1           + STRESS_DEV(3)**2 + 2.0D0*(STRESS_DEV(4)**2  
     2           + STRESS_DEV(5)**2 + STRESS_DEV(6)**2))  
C  
C-----------------------------------------------------------------------  
C  CALCULATE CURRENT YIELD STRESS  
C-----------------------------------------------------------------------  
      IF (EQPLAS .LE. TOLER) THEN  
        YIELD_STRESS = SIGMA_Y  
        HARD_MOD = 0.0D0  
      ELSE  
        YIELD_STRESS = SIGMA_Y + K*(EQPLAS**n)  
        HARD_MOD = K*n*(EQPLAS**(n-1.0D0))  
      END IF  
C  
C-----------------------------------------------------------------------  
C  YIELD CHECK  
C-----------------------------------------------------------------------  
      PHI = SMIS_TRIAL - SQRT_2_3*YIELD_STRESS  
C  
      IF (PHI .LE. TOLER) THEN  
C       Elastic step  
        DEQPL = 0.0D0  
        DO I = 1, NTENS  
          STRESS(I) = STRESS_DEV(I)  
        END DO  
        DO I = 1, NDI  
          STRESS(I) = STRESS(I) + P_TRIAL  
        END DO  
      ELSE  
C       Plastic step - Radial return  
C-----------------------------------------------------------------------  
C  CALCULATE PLASTIC MULTIPLIER INCREMENT  
C-----------------------------------------------------------------------  
        DEQPL = PHI / (2.0D0*G + 2.0D0*HARD_MOD/3.0D0)  
        DGAMMA = 1.5D0*DEQPL  
C  
C-----------------------------------------------------------------------  
C  UPDATE EQUIVALENT PLASTIC STRAIN  
C-----------------------------------------------------------------------  
        EQPLAS = EQPLAS + DEQPL  
        STATEV(1) = EQPLAS  
C  
C-----------------------------------------------------------------------  
C  CHECK FOR FAILURE  
C-----------------------------------------------------------------------  
        IF (EQPLAS .GE. EPS_FAIL) THEN  
          FAILURE_FLAG = 1.0D0  
          STATEV(2) = FAILURE_FLAG  
          DO I = 1, NTENS  
            STRESS(I) = 0.0D0  
          END DO  
          DO I = 1, NTENS  
            DO J = 1, NTENS  
              DDSDDE(I,J) = 1.0D0  
            END DO  
          END DO  
          GOTO 999  
        END IF  
C  
C-----------------------------------------------------------------------  
C  UPDATE STRESS  
C-----------------------------------------------------------------------  
        FACTOR = 1.0D0 - 2.0D0*G*DGAMMA/SMIS_TRIAL  
        ONEMFAC = 1.0D0 - FACTOR  
C  
        DO I = 1, NTENS  
          STRESS(I) = FACTOR*STRESS_DEV(I)  
        END DO  
        DO I = 1, NDI  
          STRESS(I) = STRESS(I) + P_TRIAL  
        END DO  
C  
      END IF  
C  
C-----------------------------------------------------------------------  
C  CALCULATE CONSISTENT TANGENT MODULUS (JACOBIAN MATRIX)  
C-----------------------------------------------------------------------  
C  Initialize  
      DO I = 1, NTENS  
        DO J = 1, NTENS  
          DDSDDE(I,J) = 0.0D0  
        END DO  
      END DO  
C  
      IF (PHI .LE. TOLER) THEN  
C       Elastic Jacobian  
        DO I = 1, NDI  
          DO J = 1, NDI  
            DDSDDE(I,J) = LAM  
          END DO  
          DDSDDE(I,I) = LAM + 2.0D0*G  
        END DO  
        DO I = NDI+1, NTENS  
          DDSDDE(I,I) = G  
        END DO  
      ELSE  
C       Elastoplastic consistent tangent  
        TERM1 = 2.0D0*G*FACTOR  
        TERM2 = 2.0D0*G*(ONEMFAC - DGAMMA/SMIS_TRIAL)  
     1        / (1.0D0 + HARD_MOD/(3.0D0*G))  
C  
C       Jacobian for deviatoric stress part  
        DO I = 1, NDI  
          DO J = 1, NDI  
            DDSDDE(I,J) = -TERM1/3.0D0 - TERM2*STRESS_DEV(I)  
     1                    *STRESS_DEV(J)/(SMIS_TRIAL**2)  
          END DO  
          DDSDDE(I,I) = DDSDDE(I,I) + TERM1  
        END DO  
C  
C       Volumetric part  
        DO I = 1, NDI  
          DO J = 1, NDI  
            DDSDDE(I,J) = DDSDDE(I,J) + KMOD  
          END DO  
        END DO  
C  
C       Shear part  
        DO I = NDI+1, NTENS  
          DDSDDE(I,I) = TERM1/2.0D0  
          DO J = NDI+1, NTENS  
            DDSDDE(I,J) = DDSDDE(I,J) - TERM2*STRESS_DEV(I)  
     1                    *STRESS_DEV(J)/(SMIS_TRIAL**2)  
          END DO  
        END DO  
      END IF  
C  
C-----------------------------------------------------------------------  
C  PLASTIC DISSIPATION WORK  
C-----------------------------------------------------------------------  
      SPD = YIELD_STRESS*DEQPL/DTIME  
C  
  999 CONTINUE  
      RETURN  
      END  
