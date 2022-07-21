from promo_scheduling.entity import Mechanic, Partner, Promotion

dz_1 = Mechanic('DZ 1', 10)
dz_4 = Mechanic('DZ 4')
dz_8 = Mechanic('DZ 8')

amz = Partner('Amazon')
nike = Partner('Nike')
acom = Partner('Americanas')
suba = Partner('Submarino')

amz_jobs = [
    Promotion(
        partner=amz,
        mechanic=dz_1,
        productivity=1000
    ),
    Promotion(
        partner=amz,
        mechanic=dz_4,
        productivity=3000
    ),
    Promotion(
        partner=amz,
        mechanic=dz_8,
        productivity=5000
    )
]
nike_jobs = [
    Promotion(
        partner=nike,
        mechanic=dz_1,
        productivity=2000
    ),
    Promotion(
        partner=nike,
        mechanic=dz_4,
        productivity=5000
    ),
    Promotion(
        partner=nike,
        mechanic=dz_8,
        productivity=6000
    )
]
acom_jobs = [
    Promotion(
        partner=acom,
        mechanic=dz_1,
        productivity=5000
    ),
    Promotion(
        partner=acom,
        mechanic=dz_4,
        productivity=10000
    ),
    Promotion(
        partner=acom,
        mechanic=dz_8,
        productivity=15000
    )
]

suba_jobs = [
    Promotion(
        partner=suba,
        mechanic=dz_1,
        productivity=5000
    ),
    Promotion(
        partner=suba,
        mechanic=dz_4,
        productivity=10000
    ),
    Promotion(
        partner=suba,
        mechanic=dz_8,
        productivity=15000
    )
]

possible_promotions = [*amz_jobs, *nike_jobs, *acom_jobs, *suba_jobs]
partners = [amz, nike, acom, suba]
mechanics = [dz_1, dz_4, dz_8]
