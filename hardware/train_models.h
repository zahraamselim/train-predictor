#ifndef TRAIN_MODELS_H
#define TRAIN_MODELS_H

/*
 * PREDICTETA Prediction Model
 * Auto-generated from random forest (10 trees)
 * 
 * Feature indices:
 * [0] distance_remaining\n * [1] train_length\n * [2] last_speed\n * [3] last_accel\n * [4] speed_trend\n * [5] speed_variance\n * [6] time_variance\n * [7] avg_speed_overall\n * [8] length_speed_ratio\n * [9] distance_length_ratio\n * [10] dt_interval_0\n * [11] dt_interval_1\n * [12] avg_speed_0\n * [13] avg_speed_1
 */

float predictETA_tree0(float features[14]) {
    if (features[2] <= 47.1850f) {
        if (features[2] <= 42.0850f) {
            if (features[11] <= 8.5500f) {
                if (features[10] <= 13.1500f) {
                    if (features[2] <= 41.4900f) {
                        return 7.6500f;
                    } else {
                        return 7.5143f;
                    }
                } else {
                    if (features[2] <= 40.0250f) {
                        return 7.9444f;
                    } else {
                        return 7.8000f;
                    }
                }
            } else {
                return 8.3833f;
            }
        } else {
            if (features[2] <= 45.4350f) {
                if (features[2] <= 43.5650f) {
                    if (features[7] <= 40.2396f) {
                        return 7.4000f;
                    } else {
                        return 7.3333f;
                    }
                } else {
                    if (features[5] <= 5.5576f) {
                        if (features[6] <= 3.3312f) {
                            if (features[4] <= -0.0006f) {
                                return 7.1333f;
                            } else {
                                if (features[4] <= 0.0011f) {
                                    return 7.1000f;
                                } else {
                                    return 7.1000f;
                                }
                            }
                        } else {
                            if (features[2] <= 45.1500f) {
                                if (features[4] <= 0.2679f) {
                                    return 7.2000f;
                                } else {
                                    return 7.1556f;
                                }
                            } else {
                                return 7.1222f;
                            }
                        }
                    } else {
                        return 7.0812f;
                    }
                }
            } else {
                if (features[2] <= 46.5600f) {
                    if (features[4] <= 0.2947f) {
                        if (features[2] <= 45.9550f) {
                            if (features[2] <= 45.8150f) {
                                if (features[7] <= 45.6794f) {
                                    if (features[5] <= 0.0001f) {
                                        return 7.0714f;
                                    } else {
                                        return 7.0257f;
                                    }
                                } else {
                                    return 7.1000f;
                                }
                            } else {
                                if (features[8] <= 3.8118f) {
                                    return 7.0000f;
                                } else {
                                    return 7.0333f;
                                }
                            }
                        } else {
                            if (features[11] <= 6.9500f) {
                                return 7.0000f;
                            } else {
                                if (features[2] <= 46.2950f) {
                                    if (features[5] <= 0.0001f) {
                                        return 6.9545f;
                                    } else {
                                        return 6.9889f;
                                    }
                                } else {
                                    if (features[2] <= 46.3650f) {
                                        return 6.9000f;
                                    } else {
                                        return 6.9000f;
                                    }
                                }
                            }
                        }
                    } else {
                        if (features[2] <= 45.7400f) {
                            return 6.9125f;
                        } else {
                            return 6.8556f;
                        }
                    }
                } else {
                    if (features[4] <= 0.3339f) {
                        if (features[2] <= 46.8250f) {
                            if (features[8] <= 4.8143f) {
                                return 6.9000f;
                            } else {
                                return 6.9111f;
                            }
                        } else {
                            if (features[8] <= 3.1874f) {
                                if (features[8] <= 2.1302f) {
                                    return 6.8714f;
                                } else {
                                    return 6.9000f;
                                }
                            } else {
                                if (features[5] <= 0.0001f) {
                                    return 6.8818f;
                                } else {
                                    if (features[4] <= 0.0009f) {
                                        return 6.8000f;
                                    } else {
                                        return 6.8308f;
                                    }
                                }
                            }
                        }
                    } else {
                        return 6.6833f;
                    }
                }
            }
        }
    } else {
        if (features[2] <= 49.0300f) {
            if (features[2] <= 47.8450f) {
                if (features[12] <= 44.4992f) {
                    return 6.6667f;
                } else {
                    if (features[2] <= 47.5450f) {
                        return 6.8000f;
                    } else {
                        if (features[8] <= 3.1397f) {
                            return 6.7091f;
                        } else {
                            if (features[13] <= 47.8545f) {
                                if (features[5] <= 0.0005f) {
                                    return 6.7714f;
                                } else {
                                    return 6.7222f;
                                }
                            } else {
                                return 6.8000f;
                            }
                        }
                    }
                }
            } else {
                if (features[2] <= 48.3650f) {
                    if (features[4] <= 0.0226f) {
                        if (features[2] <= 47.8850f) {
                            return 6.7333f;
                        } else {
                            if (features[7] <= 48.2344f) {
                                if (features[2] <= 48.1750f) {
                                    if (features[13] <= 47.8545f) {
                                        return 6.6800f;
                                    } else {
                                        return 6.7000f;
                                    }
                                } else {
                                    return 6.6556f;
                                }
                            } else {
                                return 6.7000f;
                            }
                        }
                    } else {
                        return 6.6333f;
                    }
                } else {
                    if (features[5] <= 0.0001f) {
                        if (features[12] <= 48.7449f) {
                            return 6.6909f;
                        } else {
                            return 6.6000f;
                        }
                    } else {
                        if (features[2] <= 48.4850f) {
                            return 6.6286f;
                        } else {
                            if (features[5] <= 0.0004f) {
                                return 6.6000f;
                            } else {
                                return 6.5875f;
                            }
                        }
                    }
                }
            }
        } else {
            if (features[6] <= 2.6413f) {
                if (features[2] <= 49.8450f) {
                    if (features[2] <= 49.2100f) {
                        return 6.5889f;
                    } else {
                        if (features[4] <= -0.0018f) {
                            return 6.4625f;
                        } else {
                            return 6.5000f;
                        }
                    }
                } else {
                    if (features[2] <= 49.9350f) {
                        if (features[4] <= 0.0003f) {
                            if (features[5] <= 0.0004f) {
                                if (features[8] <= 3.0045f) {
                                    return 6.4000f;
                                } else {
                                    return 6.4714f;
                                }
                            } else {
                                return 6.4000f;
                            }
                        } else {
                            return 6.5000f;
                        }
                    } else {
                        if (features[4] <= -0.0022f) {
                            if (features[8] <= 4.0040f) {
                                return 6.4182f;
                            } else {
                                return 6.4857f;
                            }
                        } else {
                            if (features[5] <= 0.0007f) {
                                if (features[8] <= 3.0015f) {
                                    if (features[4] <= -0.0009f) {
                                        return 6.4091f;
                                    } else {
                                        return 6.4011f;
                                    }
                                } else {
                                    if (features[8] <= 3.0027f) {
                                        return 6.4333f;
                                    } else {
                                        return 6.4122f;
                                    }
                                }
                            } else {
                                if (features[4] <= 0.0046f) {
                                    if (features[2] <= 49.9850f) {
                                        return 6.4714f;
                                    } else {
                                        return 6.4250f;
                                    }
                                } else {
                                    if (features[9] <= 1.8783f) {
                                        return 6.4167f;
                                    } else {
                                        return 6.4000f;
                                    }
                                }
                            }
                        }
                    }
                }
            } else {
                if (features[4] <= 0.0852f) {
                    if (features[2] <= 49.5200f) {
                        if (features[1] <= 175.0000f) {
                            if (features[8] <= 2.0385f) {
                                return 6.5500f;
                            } else {
                                return 6.5929f;
                            }
                        } else {
                            return 6.5000f;
                        }
                    } else {
                        if (features[2] <= 49.6950f) {
                            return 6.4750f;
                        } else {
                            return 6.5000f;
                        }
                    }
                } else {
                    if (features[11] <= 6.4500f) {
                        return 6.5000f;
                    } else {
                        if (features[8] <= 5.0025f) {
                            if (features[8] <= 2.0010f) {
                                return 6.4667f;
                            } else {
                                if (features[4] <= 0.3620f) {
                                    if (features[7] <= 48.7430f) {
                                        return 6.4111f;
                                    } else {
                                        return 6.4000f;
                                    }
                                } else {
                                    return 6.4375f;
                                }
                            }
                        } else {
                            if (features[5] <= 6.4639f) {
                                return 6.4625f;
                            } else {
                                return 6.5000f;
                            }
                        }
                    }
                }
            }
        }
    }
}

float predictETA_tree1(float features[14]) {
    if (features[2] <= 47.2000f) {
        if (features[2] <= 42.0550f) {
            if (features[10] <= 13.9500f) {
                if (features[2] <= 40.5100f) {
                    if (features[2] <= 39.7100f) {
                        return 8.0167f;
                    } else {
                        return 7.8083f;
                    }
                } else {
                    if (features[2] <= 41.0450f) {
                        return 7.7000f;
                    } else {
                        if (features[2] <= 41.7800f) {
                            return 7.5714f;
                        } else {
                            return 7.5000f;
                        }
                    }
                }
            } else {
                return 8.7000f;
            }
        } else {
            if (features[2] <= 45.8100f) {
                if (features[2] <= 43.5650f) {
                    if (features[2] <= 42.8250f) {
                        return 7.3857f;
                    } else {
                        return 7.3333f;
                    }
                } else {
                    if (features[2] <= 45.1450f) {
                        if (features[11] <= 7.1500f) {
                            return 7.2000f;
                        } else {
                            if (features[2] <= 44.1500f) {
                                return 7.1643f;
                            } else {
                                if (features[5] <= 0.0004f) {
                                    return 7.1300f;
                                } else {
                                    if (features[8] <= 4.4599f) {
                                        return 7.1000f;
                                    } else {
                                        return 7.0750f;
                                    }
                                }
                            }
                        }
                    } else {
                        if (features[4] <= 0.1451f) {
                            if (features[2] <= 45.5550f) {
                                if (features[8] <= 5.5182f) {
                                    return 7.1000f;
                                } else {
                                    return 7.1600f;
                                }
                            } else {
                                if (features[7] <= 45.6794f) {
                                    if (features[8] <= 4.3807f) {
                                        return 7.0545f;
                                    } else {
                                        return 7.0250f;
                                    }
                                } else {
                                    return 7.1000f;
                                }
                            }
                        } else {
                            if (features[4] <= 0.2966f) {
                                return 7.0000f;
                            } else {
                                return 6.9111f;
                            }
                        }
                    }
                }
            } else {
                if (features[2] <= 46.5600f) {
                    if (features[10] <= 11.0500f) {
                        if (features[2] <= 46.1250f) {
                            if (features[5] <= 0.0002f) {
                                if (features[2] <= 45.9550f) {
                                    return 7.0250f;
                                } else {
                                    return 7.0000f;
                                }
                            } else {
                                return 7.0000f;
                            }
                        } else {
                            if (features[13] <= 46.4772f) {
                                if (features[4] <= 0.0023f) {
                                    if (features[5] <= 0.0000f) {
                                        return 6.9250f;
                                    } else {
                                        return 6.9000f;
                                    }
                                } else {
                                    return 6.9600f;
                                }
                            } else {
                                return 6.9909f;
                            }
                        }
                    } else {
                        if (features[5] <= 7.6135f) {
                            return 6.9000f;
                        } else {
                            return 6.8333f;
                        }
                    }
                } else {
                    if (features[5] <= 7.1167f) {
                        if (features[2] <= 46.9450f) {
                            if (features[4] <= -0.0020f) {
                                return 6.8286f;
                            } else {
                                if (features[12] <= 45.5409f) {
                                    return 6.8429f;
                                } else {
                                    if (features[1] <= 225.0000f) {
                                        return 6.8933f;
                                    } else {
                                        return 6.9286f;
                                    }
                                }
                            }
                        } else {
                            if (features[7] <= 47.2370f) {
                                if (features[5] <= 0.0004f) {
                                    return 6.8000f;
                                } else {
                                    return 6.8400f;
                                }
                            } else {
                                return 6.9000f;
                            }
                        }
                    } else {
                        return 6.7091f;
                    }
                }
            }
        }
    } else {
        if (features[2] <= 48.9650f) {
            if (features[2] <= 48.1700f) {
                if (features[10] <= 11.0500f) {
                    if (features[2] <= 47.7950f) {
                        if (features[2] <= 47.5500f) {
                            if (features[12] <= 47.3182f) {
                                return 6.8000f;
                            } else {
                                return 6.8000f;
                            }
                        } else {
                            if (features[7] <= 47.6422f) {
                                if (features[5] <= 0.0003f) {
                                    return 6.7222f;
                                } else {
                                    return 6.7500f;
                                }
                            } else {
                                return 6.7900f;
                            }
                        }
                    } else {
                        if (features[2] <= 47.8800f) {
                            if (features[8] <= 3.6593f) {
                                return 6.7125f;
                            } else {
                                return 6.7571f;
                            }
                        } else {
                            if (features[5] <= 0.0007f) {
                                return 6.7000f;
                            } else {
                                return 6.7111f;
                            }
                        }
                    }
                } else {
                    return 6.6100f;
                }
            } else {
                if (features[2] <= 48.5150f) {
                    if (features[7] <= 48.2344f) {
                        if (features[8] <= 4.1395f) {
                            return 6.6083f;
                        } else {
                            return 6.6571f;
                        }
                    } else {
                        if (features[2] <= 48.3700f) {
                            if (features[4] <= -0.0009f) {
                                return 6.6900f;
                            } else {
                                return 6.7000f;
                            }
                        } else {
                            if (features[11] <= 6.6500f) {
                                return 6.7000f;
                            } else {
                                return 6.6222f;
                            }
                        }
                    }
                } else {
                    if (features[8] <= 4.1021f) {
                        if (features[4] <= 0.0024f) {
                            if (features[6] <= 2.6413f) {
                                return 6.6000f;
                            } else {
                                if (features[2] <= 48.7000f) {
                                    return 6.6000f;
                                } else {
                                    return 6.6000f;
                                }
                            }
                        } else {
                            return 6.5750f;
                        }
                    } else {
                        return 6.6500f;
                    }
                }
            }
        } else {
            if (features[6] <= 2.6413f) {
                if (features[2] <= 49.9050f) {
                    if (features[4] <= -0.0015f) {
                        if (features[2] <= 49.7900f) {
                            return 6.4571f;
                        } else {
                            return 6.4000f;
                        }
                    } else {
                        if (features[2] <= 49.2100f) {
                            return 6.5714f;
                        } else {
                            if (features[5] <= 0.0004f) {
                                if (features[13] <= 49.3158f) {
                                    return 6.5000f;
                                } else {
                                    return 6.5000f;
                                }
                            } else {
                                return 6.4889f;
                            }
                        }
                    }
                } else {
                    if (features[4] <= -0.0022f) {
                        if (features[8] <= 4.0040f) {
                            if (features[4] <= -0.0028f) {
                                return 6.4100f;
                            } else {
                                return 6.4429f;
                            }
                        } else {
                            return 6.4818f;
                        }
                    } else {
                        if (features[5] <= 0.0004f) {
                            if (features[8] <= 5.0005f) {
                                if (features[5] <= 0.0000f) {
                                    return 6.4300f;
                                } else {
                                    if (features[2] <= 49.9450f) {
                                        return 6.4167f;
                                    } else {
                                        return 6.4032f;
                                    }
                                }
                            } else {
                                if (features[5] <= 0.0002f) {
                                    if (features[5] <= 0.0001f) {
                                        return 6.4139f;
                                    } else {
                                        return 6.4000f;
                                    }
                                } else {
                                    if (features[8] <= 5.0045f) {
                                        return 6.4375f;
                                    } else {
                                        return 6.4125f;
                                    }
                                }
                            }
                        } else {
                            if (features[2] <= 49.9750f) {
                                if (features[5] <= 0.0008f) {
                                    return 6.4750f;
                                } else {
                                    return 6.4182f;
                                }
                            } else {
                                if (features[4] <= 0.0028f) {
                                    return 6.4071f;
                                } else {
                                    if (features[8] <= 3.5006f) {
                                        return 6.4000f;
                                    } else {
                                        return 6.4000f;
                                    }
                                }
                            }
                        }
                    }
                }
            } else {
                if (features[2] <= 49.3550f) {
                    if (features[11] <= 6.5500f) {
                        if (features[2] <= 49.2300f) {
                            return 6.6000f;
                        } else {
                            return 6.5800f;
                        }
                    } else {
                        if (features[2] <= 49.0650f) {
                            return 6.5545f;
                        } else {
                            return 6.4857f;
                        }
                    }
                } else {
                    if (features[11] <= 6.4500f) {
                        if (features[10] <= 9.7500f) {
                            return 6.5000f;
                        } else {
                            return 6.5000f;
                        }
                    } else {
                        if (features[2] <= 49.7400f) {
                            if (features[2] <= 49.6450f) {
                                if (features[2] <= 49.4600f) {
                                    return 6.5125f;
                                } else {
                                    if (features[8] <= 4.0331f) {
                                        return 6.5000f;
                                    } else {
                                        return 6.5000f;
                                    }
                                }
                            } else {
                                return 6.4636f;
                            }
                        } else {
                            if (features[7] <= 48.7384f) {
                                if (features[5] <= 5.7601f) {
                                    return 6.4778f;
                                } else {
                                    return 6.4400f;
                                }
                            } else {
                                if (features[8] <= 3.0009f) {
                                    return 6.4125f;
                                } else {
                                    if (features[6] <= 2.8063f) {
                                        return 6.4000f;
                                    } else {
                                        return 6.4000f;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

float predictETA_tree2(float features[14]) {
    if (features[2] <= 43.4350f) {
        if (features[2] <= 38.9650f) {
            if (features[10] <= 14.5500f) {
                return 8.2812f;
            } else {
                return 9.0100f;
            }
        } else {
            if (features[2] <= 41.1150f) {
                if (features[2] <= 39.9700f) {
                    return 7.9444f;
                } else {
                    if (features[2] <= 40.7550f) {
                        return 7.7900f;
                    } else {
                        return 7.7143f;
                    }
                }
            } else {
                if (features[2] <= 42.0350f) {
                    if (features[2] <= 41.5750f) {
                        return 7.5800f;
                    } else {
                        return 7.5091f;
                    }
                } else {
                    if (features[2] <= 42.7900f) {
                        return 7.3818f;
                    } else {
                        return 7.3167f;
                    }
                }
            }
        }
    } else {
        if (features[2] <= 47.8750f) {
            if (features[2] <= 46.4750f) {
                if (features[2] <= 45.4350f) {
                    if (features[4] <= 0.3157f) {
                        if (features[6] <= 3.3312f) {
                            if (features[8] <= 5.5182f) {
                                if (features[4] <= -0.0008f) {
                                    return 7.1000f;
                                } else {
                                    if (features[5] <= 0.0003f) {
                                        return 7.1000f;
                                    } else {
                                        return 7.1000f;
                                    }
                                }
                            } else {
                                return 7.1462f;
                            }
                        } else {
                            if (features[2] <= 45.1700f) {
                                if (features[4] <= 0.2760f) {
                                    return 7.2000f;
                                } else {
                                    return 7.1364f;
                                }
                            } else {
                                return 7.1143f;
                            }
                        }
                    } else {
                        return 7.0700f;
                    }
                } else {
                    if (features[4] <= 0.2958f) {
                        if (features[2] <= 45.8450f) {
                            if (features[11] <= 7.0500f) {
                                return 7.0900f;
                            } else {
                                if (features[2] <= 45.7100f) {
                                    if (features[10] <= 10.6500f) {
                                        return 7.0789f;
                                    } else {
                                        return 7.0211f;
                                    }
                                } else {
                                    return 7.0000f;
                                }
                            }
                        } else {
                            if (features[2] <= 46.1000f) {
                                return 7.0000f;
                            } else {
                                if (features[13] <= 46.4772f) {
                                    if (features[8] <= 3.7818f) {
                                        return 6.9640f;
                                    } else {
                                        return 6.9056f;
                                    }
                                } else {
                                    return 7.0000f;
                                }
                            }
                        }
                    } else {
                        return 6.8600f;
                    }
                }
            } else {
                if (features[2] <= 47.0050f) {
                    if (features[11] <= 7.0500f) {
                        if (features[4] <= -0.0017f) {
                            return 6.8250f;
                        } else {
                            if (features[2] <= 46.6550f) {
                                if (features[11] <= 6.9500f) {
                                    return 6.9667f;
                                } else {
                                    return 6.9000f;
                                }
                            } else {
                                if (features[2] <= 46.9350f) {
                                    if (features[2] <= 46.8050f) {
                                        return 6.9000f;
                                    } else {
                                        return 6.9000f;
                                    }
                                } else {
                                    return 6.8833f;
                                }
                            }
                        }
                    } else {
                        return 6.7333f;
                    }
                } else {
                    if (features[4] <= 0.2934f) {
                        if (features[2] <= 47.5450f) {
                            if (features[2] <= 47.1100f) {
                                return 6.8357f;
                            } else {
                                if (features[2] <= 47.1800f) {
                                    return 6.8143f;
                                } else {
                                    return 6.8000f;
                                }
                            }
                        } else {
                            if (features[13] <= 47.8545f) {
                                if (features[8] <= 4.7160f) {
                                    if (features[5] <= 0.0002f) {
                                        return 6.7000f;
                                    } else {
                                        return 6.7250f;
                                    }
                                } else {
                                    return 6.7545f;
                                }
                            } else {
                                if (features[1] <= 175.0000f) {
                                    return 6.7571f;
                                } else {
                                    return 6.8000f;
                                }
                            }
                        }
                    } else {
                        return 6.6467f;
                    }
                }
            }
        } else {
            if (features[2] <= 49.2600f) {
                if (features[2] <= 48.6650f) {
                    if (features[8] <= 4.1558f) {
                        if (features[2] <= 48.4750f) {
                            if (features[5] <= 0.0067f) {
                                if (features[2] <= 48.0700f) {
                                    return 6.7000f;
                                } else {
                                    if (features[7] <= 48.2344f) {
                                        return 6.6375f;
                                    } else {
                                        return 6.6800f;
                                    }
                                }
                            } else {
                                return 6.6286f;
                            }
                        } else {
                            if (features[5] <= 0.0001f) {
                                return 6.6429f;
                            } else {
                                return 6.5875f;
                            }
                        }
                    } else {
                        if (features[5] <= 0.0007f) {
                            if (features[4] <= 0.0003f) {
                                return 6.7000f;
                            } else {
                                return 6.7000f;
                            }
                        } else {
                            return 6.7429f;
                        }
                    }
                } else {
                    if (features[2] <= 49.0650f) {
                        if (features[2] <= 48.9650f) {
                            return 6.6000f;
                        } else {
                            if (features[2] <= 49.0050f) {
                                return 6.5667f;
                            } else {
                                return 6.5909f;
                            }
                        }
                    } else {
                        if (features[6] <= 2.8063f) {
                            return 6.5200f;
                        } else {
                            return 6.6000f;
                        }
                    }
                }
            } else {
                if (features[6] <= 2.6413f) {
                    if (features[2] <= 49.9050f) {
                        if (features[4] <= -0.0018f) {
                            return 6.4333f;
                        } else {
                            if (features[5] <= 0.0005f) {
                                if (features[2] <= 49.4950f) {
                                    return 6.5000f;
                                } else {
                                    return 6.5000f;
                                }
                            } else {
                                return 6.4833f;
                            }
                        }
                    } else {
                        if (features[2] <= 49.9450f) {
                            if (features[5] <= 0.0002f) {
                                return 6.4100f;
                            } else {
                                if (features[2] <= 49.9350f) {
                                    if (features[5] <= 0.0005f) {
                                        return 6.4778f;
                                    } else {
                                        return 6.4118f;
                                    }
                                } else {
                                    return 6.4692f;
                                }
                            }
                        } else {
                            if (features[2] <= 49.9850f) {
                                if (features[5] <= 0.0006f) {
                                    if (features[5] <= 0.0003f) {
                                        return 6.4157f;
                                    } else {
                                        return 6.4021f;
                                    }
                                } else {
                                    if (features[2] <= 49.9750f) {
                                        return 6.4500f;
                                    } else {
                                        return 6.4077f;
                                    }
                                }
                            } else {
                                if (features[8] <= 5.0005f) {
                                    if (features[5] <= 0.0002f) {
                                        return 6.4040f;
                                    } else {
                                        return 6.4000f;
                                    }
                                } else {
                                    return 6.4154f;
                                }
                            }
                        }
                    }
                } else {
                    if (features[5] <= 0.9019f) {
                        if (features[2] <= 49.4200f) {
                            return 6.5750f;
                        } else {
                            if (features[2] <= 49.5050f) {
                                return 6.5167f;
                            } else {
                                if (features[2] <= 49.6950f) {
                                    if (features[2] <= 49.5850f) {
                                        return 6.5000f;
                                    } else {
                                        return 6.4667f;
                                    }
                                } else {
                                    return 6.5000f;
                                }
                            }
                        }
                    } else {
                        if (features[6] <= 2.9763f) {
                            if (features[8] <= 3.0009f) {
                                return 6.4429f;
                            } else {
                                return 6.4000f;
                            }
                        } else {
                            if (features[1] <= 175.0000f) {
                                if (features[1] <= 125.0000f) {
                                    return 6.4778f;
                                } else {
                                    return 6.4200f;
                                }
                            } else {
                                if (features[10] <= 10.5000f) {
                                    if (features[5] <= 5.3842f) {
                                        return 6.4714f;
                                    } else {
                                        return 6.5000f;
                                    }
                                } else {
                                    return 6.4500f;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

float predictETA_tree3(float features[14]) {
    if (features[2] <= 46.5650f) {
        if (features[2] <= 41.6550f) {
            if (features[2] <= 38.0600f) {
                return 8.7800f;
            } else {
                if (features[2] <= 39.9350f) {
                    if (features[2] <= 38.9650f) {
                        return 8.1500f;
                    } else {
                        return 7.9692f;
                    }
                } else {
                    if (features[2] <= 41.0450f) {
                        if (features[2] <= 40.5100f) {
                            return 7.8000f;
                        } else {
                            return 7.7100f;
                        }
                    } else {
                        return 7.5900f;
                    }
                }
            }
        } else {
            if (features[2] <= 43.4350f) {
                if (features[2] <= 42.1100f) {
                    return 7.5000f;
                } else {
                    if (features[2] <= 42.8600f) {
                        if (features[5] <= 5.9439f) {
                            return 7.4000f;
                        } else {
                            return 7.3833f;
                        }
                    } else {
                        return 7.3000f;
                    }
                }
            } else {
                if (features[2] <= 45.6700f) {
                    if (features[4] <= 0.3322f) {
                        if (features[2] <= 45.4050f) {
                            if (features[6] <= 3.3312f) {
                                if (features[2] <= 45.0650f) {
                                    return 7.1333f;
                                } else {
                                    if (features[7] <= 45.2010f) {
                                        return 7.1000f;
                                    } else {
                                        return 7.1000f;
                                    }
                                }
                            } else {
                                if (features[4] <= 0.2830f) {
                                    if (features[2] <= 45.1700f) {
                                        return 7.1941f;
                                    } else {
                                        return 7.1286f;
                                    }
                                } else {
                                    if (features[7] <= 41.8872f) {
                                        return 7.1200f;
                                    } else {
                                        return 7.0875f;
                                    }
                                }
                            }
                        } else {
                            if (features[7] <= 45.5169f) {
                                if (features[4] <= 0.0014f) {
                                    return 7.0333f;
                                } else {
                                    return 6.9833f;
                                }
                            } else {
                                if (features[5] <= 0.0002f) {
                                    return 7.0833f;
                                } else {
                                    return 7.1000f;
                                }
                            }
                        }
                    } else {
                        return 6.9625f;
                    }
                } else {
                    if (features[2] <= 46.1000f) {
                        if (features[7] <= 43.9292f) {
                            return 6.9000f;
                        } else {
                            if (features[4] <= 0.0014f) {
                                if (features[6] <= 3.1513f) {
                                    return 7.0000f;
                                } else {
                                    if (features[5] <= 0.0001f) {
                                        return 7.0286f;
                                    } else {
                                        return 7.0000f;
                                    }
                                }
                            } else {
                                if (features[4] <= 0.0040f) {
                                    return 7.0750f;
                                } else {
                                    return 7.0125f;
                                }
                            }
                        }
                    } else {
                        if (features[13] <= 46.4772f) {
                            if (features[2] <= 46.2750f) {
                                if (features[8] <= 3.2439f) {
                                    return 6.9571f;
                                } else {
                                    return 6.9100f;
                                }
                            } else {
                                if (features[4] <= 0.0003f) {
                                    return 6.9000f;
                                } else {
                                    return 6.8800f;
                                }
                            }
                        } else {
                            if (features[2] <= 46.4250f) {
                                return 7.0000f;
                            } else {
                                return 6.9750f;
                            }
                        }
                    }
                }
            }
        }
    } else {
        if (features[2] <= 48.6450f) {
            if (features[2] <= 47.3550f) {
                if (features[4] <= 0.3451f) {
                    if (features[2] <= 46.9450f) {
                        if (features[5] <= 0.0016f) {
                            if (features[2] <= 46.8050f) {
                                if (features[5] <= 0.0002f) {
                                    return 6.9000f;
                                } else {
                                    return 6.9143f;
                                }
                            } else {
                                return 6.8800f;
                            }
                        } else {
                            return 6.8400f;
                        }
                    } else {
                        if (features[2] <= 47.1900f) {
                            if (features[6] <= 2.9763f) {
                                return 6.8118f;
                            } else {
                                return 6.8818f;
                            }
                        } else {
                            return 6.8000f;
                        }
                    }
                } else {
                    return 6.6909f;
                }
            } else {
                if (features[2] <= 47.8750f) {
                    if (features[5] <= 5.9444f) {
                        if (features[5] <= 0.0001f) {
                            return 6.7154f;
                        } else {
                            if (features[7] <= 47.8194f) {
                                if (features[2] <= 47.5700f) {
                                    if (features[8] <= 3.1649f) {
                                        return 6.8000f;
                                    } else {
                                        return 6.7667f;
                                    }
                                } else {
                                    if (features[2] <= 47.7250f) {
                                        return 6.7429f;
                                    } else {
                                        return 6.7000f;
                                    }
                                }
                            } else {
                                return 6.8000f;
                            }
                        }
                    } else {
                        return 6.6125f;
                    }
                } else {
                    if (features[8] <= 3.1204f) {
                        if (features[2] <= 48.4850f) {
                            if (features[11] <= 6.7500f) {
                                if (features[4] <= -0.0018f) {
                                    return 6.6455f;
                                } else {
                                    if (features[8] <= 3.0969f) {
                                        return 6.7000f;
                                    } else {
                                        return 6.6667f;
                                    }
                                }
                            } else {
                                return 6.6125f;
                            }
                        } else {
                            return 6.5875f;
                        }
                    } else {
                        if (features[2] <= 48.2400f) {
                            if (features[5] <= 0.0001f) {
                                return 6.7250f;
                            } else {
                                if (features[5] <= 0.0007f) {
                                    if (features[5] <= 0.0003f) {
                                        return 6.7000f;
                                    } else {
                                        return 6.7000f;
                                    }
                                } else {
                                    return 6.7143f;
                                }
                            }
                        } else {
                            if (features[11] <= 6.6500f) {
                                return 6.7000f;
                            } else {
                                return 6.6600f;
                            }
                        }
                    }
                }
            }
        } else {
            if (features[6] <= 2.6413f) {
                if (features[2] <= 49.5950f) {
                    if (features[2] <= 49.1950f) {
                        return 6.6000f;
                    } else {
                        return 6.5000f;
                    }
                } else {
                    if (features[2] <= 49.9550f) {
                        if (features[4] <= 0.0015f) {
                            if (features[8] <= 3.0111f) {
                                if (features[9] <= 2.6833f) {
                                    if (features[5] <= 0.0002f) {
                                        return 6.4000f;
                                    } else {
                                        return 6.4286f;
                                    }
                                } else {
                                    if (features[5] <= 0.0002f) {
                                        return 6.4167f;
                                    } else {
                                        return 6.4000f;
                                    }
                                }
                            } else {
                                if (features[5] <= 0.0006f) {
                                    if (features[2] <= 49.9350f) {
                                        return 6.4737f;
                                    } else {
                                        return 6.4389f;
                                    }
                                } else {
                                    return 6.4143f;
                                }
                            }
                        } else {
                            return 6.5000f;
                        }
                    } else {
                        if (features[8] <= 5.0015f) {
                            if (features[5] <= 0.0002f) {
                                if (features[4] <= 0.0015f) {
                                    if (features[4] <= 0.0003f) {
                                        return 6.4082f;
                                    } else {
                                        return 6.4000f;
                                    }
                                } else {
                                    return 6.4250f;
                                }
                            } else {
                                if (features[5] <= 0.0007f) {
                                    return 6.4000f;
                                } else {
                                    if (features[5] <= 0.0010f) {
                                        return 6.4167f;
                                    } else {
                                        return 6.4000f;
                                    }
                                }
                            }
                        } else {
                            if (features[5] <= 0.0001f) {
                                return 6.4118f;
                            } else {
                                if (features[8] <= 5.0035f) {
                                    if (features[4] <= -0.0009f) {
                                        return 6.4214f;
                                    } else {
                                        return 6.4375f;
                                    }
                                } else {
                                    return 6.4500f;
                                }
                            }
                        }
                    }
                }
            } else {
                if (features[2] <= 49.2950f) {
                    if (features[2] <= 48.9950f) {
                        if (features[5] <= 0.0012f) {
                            if (features[4] <= -0.0015f) {
                                return 6.6000f;
                            } else {
                                if (features[1] <= 175.0000f) {
                                    return 6.6000f;
                                } else {
                                    return 6.6000f;
                                }
                            }
                        } else {
                            return 6.5833f;
                        }
                    } else {
                        if (features[7] <= 49.0304f) {
                            if (features[8] <= 3.5604f) {
                                return 6.5375f;
                            } else {
                                return 6.5000f;
                            }
                        } else {
                            return 6.6000f;
                        }
                    }
                } else {
                    if (features[5] <= 0.7856f) {
                        if (features[2] <= 49.5200f) {
                            return 6.5231f;
                        } else {
                            if (features[2] <= 49.6950f) {
                                return 6.4846f;
                            } else {
                                return 6.5000f;
                            }
                        }
                    } else {
                        if (features[8] <= 5.0025f) {
                            if (features[8] <= 2.0010f) {
                                return 6.4800f;
                            } else {
                                if (features[10] <= 9.9500f) {
                                    if (features[5] <= 2.1704f) {
                                        return 6.4000f;
                                    } else {
                                        return 6.4125f;
                                    }
                                } else {
                                    if (features[7] <= 48.2767f) {
                                        return 6.4188f;
                                    } else {
                                        return 6.5000f;
                                    }
                                }
                            }
                        } else {
                            return 6.5000f;
                        }
                    }
                }
            }
        }
    }
}

float predictETA_tree4(float features[14]) {
    if (features[2] <= 43.4650f) {
        if (features[10] <= 14.3000f) {
            if (features[2] <= 41.0450f) {
                if (features[2] <= 39.7100f) {
                    return 8.1154f;
                } else {
                    if (features[2] <= 40.5100f) {
                        return 7.8200f;
                    } else {
                        return 7.7333f;
                    }
                }
            } else {
                if (features[2] <= 42.0550f) {
                    if (features[2] <= 41.5750f) {
                        return 7.6000f;
                    } else {
                        return 7.5000f;
                    }
                } else {
                    if (features[2] <= 42.9500f) {
                        return 7.3833f;
                    } else {
                        return 7.3000f;
                    }
                }
            }
        } else {
            return 8.9933f;
        }
    } else {
        if (features[2] <= 47.8450f) {
            if (features[2] <= 46.0950f) {
                if (features[2] <= 45.4350f) {
                    if (features[4] <= 0.3109f) {
                        if (features[2] <= 45.1450f) {
                            if (features[13] <= 45.1770f) {
                                if (features[7] <= 41.5165f) {
                                    return 7.1778f;
                                } else {
                                    if (features[8] <= 4.4539f) {
                                        return 7.1000f;
                                    } else {
                                        return 7.0833f;
                                    }
                                }
                            } else {
                                return 7.2000f;
                            }
                        } else {
                            if (features[5] <= 0.0001f) {
                                return 7.1417f;
                            } else {
                                if (features[4] <= 0.0014f) {
                                    if (features[1] <= 175.0000f) {
                                        return 7.1000f;
                                    } else {
                                        return 7.1000f;
                                    }
                                } else {
                                    return 7.0857f;
                                }
                            }
                        }
                    } else {
                        return 7.0167f;
                    }
                } else {
                    if (features[4] <= 0.2947f) {
                        if (features[2] <= 45.8650f) {
                            if (features[11] <= 7.0500f) {
                                return 7.1000f;
                            } else {
                                if (features[2] <= 45.5800f) {
                                    if (features[7] <= 45.5169f) {
                                        return 7.0222f;
                                    } else {
                                        return 7.1000f;
                                    }
                                } else {
                                    if (features[2] <= 45.7100f) {
                                        return 7.0250f;
                                    } else {
                                        return 7.0000f;
                                    }
                                }
                            }
                        } else {
                            if (features[5] <= 0.0000f) {
                                return 7.0250f;
                            } else {
                                if (features[7] <= 46.0577f) {
                                    return 7.0000f;
                                } else {
                                    return 7.0000f;
                                }
                            }
                        }
                    } else {
                        return 6.8857f;
                    }
                }
            } else {
                if (features[2] <= 47.2000f) {
                    if (features[13] <= 45.8179f) {
                        return 6.7800f;
                    } else {
                        if (features[2] <= 46.9250f) {
                            if (features[2] <= 46.6450f) {
                                if (features[11] <= 6.9500f) {
                                    if (features[9] <= 1.4490f) {
                                        return 7.0000f;
                                    } else {
                                        return 6.9556f;
                                    }
                                } else {
                                    if (features[5] <= 0.0004f) {
                                        return 6.9065f;
                                    } else {
                                        return 6.9500f;
                                    }
                                }
                            } else {
                                if (features[7] <= 46.6691f) {
                                    return 6.8857f;
                                } else {
                                    if (features[2] <= 46.6800f) {
                                        return 6.9000f;
                                    } else {
                                        return 6.9000f;
                                    }
                                }
                            }
                        } else {
                            if (features[11] <= 6.8500f) {
                                return 6.9000f;
                            } else {
                                if (features[4] <= 0.0009f) {
                                    return 6.8071f;
                                } else {
                                    return 6.8500f;
                                }
                            }
                        }
                    }
                } else {
                    if (features[12] <= 44.4992f) {
                        return 6.6333f;
                    } else {
                        if (features[2] <= 47.5400f) {
                            return 6.8000f;
                        } else {
                            if (features[8] <= 4.1960f) {
                                if (features[2] <= 47.6850f) {
                                    return 6.7000f;
                                } else {
                                    return 6.7444f;
                                }
                            } else {
                                return 6.7875f;
                            }
                        }
                    }
                }
            }
        } else {
            if (features[2] <= 49.0250f) {
                if (features[2] <= 48.3650f) {
                    if (features[5] <= 0.0365f) {
                        if (features[2] <= 48.1300f) {
                            if (features[8] <= 4.1671f) {
                                if (features[1] <= 125.0000f) {
                                    return 6.7000f;
                                } else {
                                    return 6.7000f;
                                }
                            } else {
                                return 6.7273f;
                            }
                        } else {
                            if (features[7] <= 48.2344f) {
                                return 6.6538f;
                            } else {
                                if (features[4] <= -0.0009f) {
                                    return 6.6875f;
                                } else {
                                    return 6.7000f;
                                }
                            }
                        }
                    } else {
                        return 6.6500f;
                    }
                } else {
                    if (features[5] <= 1.3893f) {
                        if (features[8] <= 5.1319f) {
                            if (features[2] <= 48.5150f) {
                                return 6.6333f;
                            } else {
                                if (features[2] <= 48.6050f) {
                                    return 6.6000f;
                                } else {
                                    return 6.6000f;
                                }
                            }
                        } else {
                            return 6.6714f;
                        }
                    } else {
                        return 6.5250f;
                    }
                }
            } else {
                if (features[6] <= 2.6413f) {
                    if (features[2] <= 49.9050f) {
                        if (features[4] <= -0.0018f) {
                            return 6.4455f;
                        } else {
                            if (features[2] <= 49.2850f) {
                                return 6.5143f;
                            } else {
                                if (features[5] <= 0.0004f) {
                                    return 6.5000f;
                                } else {
                                    return 6.4833f;
                                }
                            }
                        }
                    } else {
                        if (features[4] <= 0.0003f) {
                            if (features[8] <= 2.0010f) {
                                return 6.4500f;
                            } else {
                                if (features[8] <= 3.0015f) {
                                    return 6.4000f;
                                } else {
                                    if (features[2] <= 49.9650f) {
                                        return 6.4311f;
                                    } else {
                                        return 6.4114f;
                                    }
                                }
                            }
                        } else {
                            if (features[4] <= 0.0034f) {
                                if (features[2] <= 49.9450f) {
                                    return 6.4250f;
                                } else {
                                    if (features[5] <= 0.0002f) {
                                        return 6.4055f;
                                    } else {
                                        return 6.4000f;
                                    }
                                }
                            } else {
                                if (features[2] <= 49.9750f) {
                                    return 6.4412f;
                                } else {
                                    if (features[2] <= 49.9850f) {
                                        return 6.4167f;
                                    } else {
                                        return 6.4000f;
                                    }
                                }
                            }
                        }
                    }
                } else {
                    if (features[5] <= 0.8834f) {
                        if (features[2] <= 49.3300f) {
                            if (features[7] <= 49.1529f) {
                                return 6.5000f;
                            } else {
                                return 6.6000f;
                            }
                        } else {
                            if (features[2] <= 49.8100f) {
                                if (features[2] <= 49.6650f) {
                                    if (features[5] <= 0.0002f) {
                                        return 6.5000f;
                                    } else {
                                        return 6.5167f;
                                    }
                                } else {
                                    return 6.4300f;
                                }
                            } else {
                                return 6.5000f;
                            }
                        }
                    } else {
                        if (features[2] <= 49.5350f) {
                            return 6.5250f;
                        } else {
                            if (features[6] <= 2.9763f) {
                                if (features[8] <= 3.0015f) {
                                    return 6.4167f;
                                } else {
                                    return 6.4000f;
                                }
                            } else {
                                if (features[1] <= 175.0000f) {
                                    if (features[5] <= 5.6610f) {
                                        return 6.4909f;
                                    } else {
                                        return 6.4143f;
                                    }
                                } else {
                                    if (features[8] <= 5.0015f) {
                                        return 6.5000f;
                                    } else {
                                        return 6.4667f;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

float predictETA_tree5(float features[14]) {
    if (features[2] <= 46.7150f) {
        if (features[2] <= 41.5750f) {
            if (features[2] <= 38.0600f) {
                return 8.7750f;
            } else {
                if (features[2] <= 39.9700f) {
                    if (features[2] <= 38.9650f) {
                        return 8.1556f;
                    } else {
                        return 7.9500f;
                    }
                } else {
                    if (features[2] <= 41.0450f) {
                        return 7.7700f;
                    } else {
                        return 7.5900f;
                    }
                }
            }
        } else {
            if (features[11] <= 7.6500f) {
                if (features[2] <= 45.8100f) {
                    if (features[2] <= 45.4200f) {
                        if (features[7] <= 45.1471f) {
                            if (features[2] <= 43.9500f) {
                                return 7.1667f;
                            } else {
                                if (features[4] <= 0.2930f) {
                                    if (features[8] <= 5.5359f) {
                                        return 7.1000f;
                                    } else {
                                        return 7.1167f;
                                    }
                                } else {
                                    return 7.0333f;
                                }
                            }
                        } else {
                            if (features[2] <= 45.2050f) {
                                return 7.2000f;
                            } else {
                                if (features[8] <= 4.4209f) {
                                    return 7.1000f;
                                } else {
                                    return 7.1200f;
                                }
                            }
                        }
                    } else {
                        if (features[5] <= 4.7278f) {
                            if (features[2] <= 45.6050f) {
                                if (features[7] <= 45.5169f) {
                                    return 7.0143f;
                                } else {
                                    return 7.1000f;
                                }
                            } else {
                                if (features[6] <= 3.1513f) {
                                    if (features[5] <= 0.0002f) {
                                        return 7.0071f;
                                    } else {
                                        return 7.0400f;
                                    }
                                } else {
                                    return 7.0750f;
                                }
                            }
                        } else {
                            return 6.9333f;
                        }
                    }
                } else {
                    if (features[6] <= 4.3112f) {
                        if (features[2] <= 46.3350f) {
                            if (features[2] <= 46.1000f) {
                                if (features[4] <= 0.0023f) {
                                    if (features[5] <= 0.0000f) {
                                        return 7.0167f;
                                    } else {
                                        return 7.0000f;
                                    }
                                } else {
                                    return 7.0429f;
                                }
                            } else {
                                if (features[5] <= 0.0001f) {
                                    return 6.9143f;
                                } else {
                                    if (features[2] <= 46.1850f) {
                                        return 6.9538f;
                                    } else {
                                        return 7.0000f;
                                    }
                                }
                            }
                        } else {
                            if (features[4] <= -0.0017f) {
                                return 6.9600f;
                            } else {
                                if (features[4] <= 0.0012f) {
                                    return 6.9000f;
                                } else {
                                    return 6.9400f;
                                }
                            }
                        }
                    } else {
                        return 6.7800f;
                    }
                }
            } else {
                if (features[2] <= 42.0300f) {
                    return 7.5000f;
                } else {
                    if (features[5] <= 6.0585f) {
                        return 7.4000f;
                    } else {
                        return 7.3300f;
                    }
                }
            }
        }
    } else {
        if (features[2] <= 48.9950f) {
            if (features[2] <= 47.8500f) {
                if (features[4] <= 0.3406f) {
                    if (features[2] <= 47.5450f) {
                        if (features[2] <= 47.1900f) {
                            if (features[7] <= 47.2370f) {
                                if (features[2] <= 46.9100f) {
                                    if (features[12] <= 46.8610f) {
                                        return 6.9000f;
                                    } else {
                                        return 6.8625f;
                                    }
                                } else {
                                    if (features[5] <= 0.0002f) {
                                        return 6.8500f;
                                    } else {
                                        return 6.8050f;
                                    }
                                }
                            } else {
                                return 6.9000f;
                            }
                        } else {
                            if (features[8] <= 3.1649f) {
                                return 6.8000f;
                            } else {
                                return 6.8000f;
                            }
                        }
                    } else {
                        if (features[7] <= 47.8194f) {
                            if (features[5] <= 0.0003f) {
                                return 6.7000f;
                            } else {
                                return 6.7273f;
                            }
                        } else {
                            return 6.7889f;
                        }
                    }
                } else {
                    return 6.6538f;
                }
            } else {
                if (features[2] <= 48.4750f) {
                    if (features[8] <= 4.1464f) {
                        if (features[5] <= 0.0003f) {
                            if (features[7] <= 48.2344f) {
                                return 6.6182f;
                            } else {
                                if (features[2] <= 48.3800f) {
                                    return 6.7000f;
                                } else {
                                    return 6.6500f;
                                }
                            }
                        } else {
                            if (features[2] <= 48.1750f) {
                                if (features[2] <= 48.0000f) {
                                    return 6.6833f;
                                } else {
                                    return 6.7000f;
                                }
                            } else {
                                return 6.6727f;
                            }
                        }
                    } else {
                        if (features[4] <= 0.0012f) {
                            if (features[8] <= 5.2072f) {
                                if (features[8] <= 5.1717f) {
                                    if (features[6] <= 2.8063f) {
                                        return 6.7000f;
                                    } else {
                                        return 6.7167f;
                                    }
                                } else {
                                    return 6.6857f;
                                }
                            } else {
                                return 6.7500f;
                            }
                        } else {
                            return 6.6667f;
                        }
                    }
                } else {
                    if (features[5] <= 0.0013f) {
                        if (features[6] <= 2.8063f) {
                            return 6.6000f;
                        } else {
                            return 6.6300f;
                        }
                    } else {
                        return 6.5750f;
                    }
                }
            }
        } else {
            if (features[6] <= 2.6413f) {
                if (features[2] <= 49.9050f) {
                    if (features[4] <= -0.0018f) {
                        return 6.4333f;
                    } else {
                        if (features[2] <= 49.3450f) {
                            return 6.5333f;
                        } else {
                            if (features[11] <= 6.5500f) {
                                return 6.5000f;
                            } else {
                                return 6.4833f;
                            }
                        }
                    }
                } else {
                    if (features[5] <= 0.0006f) {
                        if (features[8] <= 5.0065f) {
                            if (features[8] <= 3.0009f) {
                                if (features[4] <= -0.0009f) {
                                    if (features[2] <= 49.9650f) {
                                        return 6.4000f;
                                    } else {
                                        return 6.4333f;
                                    }
                                } else {
                                    if (features[2] <= 49.9550f) {
                                        return 6.4071f;
                                    } else {
                                        return 6.4000f;
                                    }
                                }
                            } else {
                                if (features[5] <= 0.0000f) {
                                    return 6.4429f;
                                } else {
                                    if (features[4] <= -0.0015f) {
                                        return 6.4294f;
                                    } else {
                                        return 6.4097f;
                                    }
                                }
                            }
                        } else {
                            return 6.4429f;
                        }
                    } else {
                        if (features[2] <= 49.9750f) {
                            if (features[5] <= 0.0008f) {
                                return 6.4778f;
                            } else {
                                if (features[4] <= 0.0009f) {
                                    return 6.4000f;
                                } else {
                                    return 6.4312f;
                                }
                            }
                        } else {
                            if (features[4] <= 0.0028f) {
                                return 6.4143f;
                            } else {
                                return 6.4000f;
                            }
                        }
                    }
                }
            } else {
                if (features[5] <= 0.2534f) {
                    if (features[2] <= 49.4450f) {
                        if (features[11] <= 6.5500f) {
                            return 6.5857f;
                        } else {
                            if (features[2] <= 49.1000f) {
                                return 6.5333f;
                            } else {
                                return 6.5000f;
                            }
                        }
                    } else {
                        if (features[2] <= 49.6950f) {
                            if (features[8] <= 2.5234f) {
                                return 6.4429f;
                            } else {
                                return 6.5067f;
                            }
                        } else {
                            if (features[4] <= -0.0028f) {
                                return 6.5000f;
                            } else {
                                return 6.5000f;
                            }
                        }
                    }
                } else {
                    if (features[11] <= 6.4500f) {
                        return 6.5000f;
                    } else {
                        if (features[7] <= 48.7879f) {
                            if (features[12] <= 46.4125f) {
                                if (features[8] <= 5.0025f) {
                                    return 6.4167f;
                                } else {
                                    return 6.4833f;
                                }
                            } else {
                                if (features[1] <= 175.0000f) {
                                    return 6.4600f;
                                } else {
                                    return 6.5083f;
                                }
                            }
                        } else {
                            if (features[9] <= 2.6833f) {
                                return 6.4000f;
                            } else {
                                return 6.4875f;
                            }
                        }
                    }
                }
            }
        }
    }
}

float predictETA_tree6(float features[14]) {
    if (features[2] <= 47.0050f) {
        if (features[2] <= 42.8600f) {
            if (features[13] <= 38.6840f) {
                if (features[2] <= 38.0600f) {
                    return 8.5143f;
                } else {
                    return 8.0889f;
                }
            } else {
                if (features[2] <= 41.0450f) {
                    if (features[10] <= 13.2500f) {
                        return 7.7714f;
                    } else {
                        return 7.8167f;
                    }
                } else {
                    if (features[2] <= 42.0850f) {
                        if (features[2] <= 41.7550f) {
                            if (features[6] <= 5.8813f) {
                                return 7.5571f;
                            } else {
                                return 7.6000f;
                            }
                        } else {
                            return 7.5000f;
                        }
                    } else {
                        if (features[7] <= 39.9341f) {
                            return 7.3857f;
                        } else {
                            return 7.4000f;
                        }
                    }
                }
            }
        } else {
            if (features[2] <= 45.9850f) {
                if (features[2] <= 45.4050f) {
                    if (features[2] <= 43.5650f) {
                        return 7.3000f;
                    } else {
                        if (features[8] <= 5.5182f) {
                            if (features[4] <= 0.2913f) {
                                if (features[6] <= 3.3312f) {
                                    if (features[1] <= 125.0000f) {
                                        return 7.1000f;
                                    } else {
                                        return 7.1000f;
                                    }
                                } else {
                                    if (features[5] <= 0.9245f) {
                                        return 7.1714f;
                                    } else {
                                        return 7.1333f;
                                    }
                                }
                            } else {
                                return 7.0500f;
                            }
                        } else {
                            if (features[7] <= 45.1471f) {
                                return 7.1364f;
                            } else {
                                return 7.1778f;
                            }
                        }
                    }
                } else {
                    if (features[5] <= 5.2556f) {
                        if (features[2] <= 45.6950f) {
                            if (features[7] <= 45.5169f) {
                                return 7.0100f;
                            } else {
                                if (features[5] <= 0.0002f) {
                                    return 7.0462f;
                                } else {
                                    return 7.1000f;
                                }
                            }
                        } else {
                            if (features[6] <= 3.1513f) {
                                return 7.0000f;
                            } else {
                                if (features[2] <= 45.8500f) {
                                    return 7.0833f;
                                } else {
                                    return 7.0083f;
                                }
                            }
                        }
                    } else {
                        return 6.9111f;
                    }
                }
            } else {
                if (features[4] <= 0.3217f) {
                    if (features[2] <= 46.4350f) {
                        if (features[11] <= 6.9500f) {
                            return 7.0000f;
                        } else {
                            if (features[2] <= 46.2400f) {
                                if (features[2] <= 46.1000f) {
                                    if (features[9] <= 1.8783f) {
                                        return 6.9625f;
                                    } else {
                                        return 7.0000f;
                                    }
                                } else {
                                    if (features[5] <= 0.0004f) {
                                        return 6.9571f;
                                    } else {
                                        return 6.9222f;
                                    }
                                }
                            } else {
                                return 6.8867f;
                            }
                        }
                    } else {
                        if (features[2] <= 46.7100f) {
                            if (features[7] <= 46.6691f) {
                                return 6.9000f;
                            } else {
                                return 6.9429f;
                            }
                        } else {
                            if (features[5] <= 0.0003f) {
                                if (features[2] <= 46.9100f) {
                                    return 6.8875f;
                                } else {
                                    return 6.8667f;
                                }
                            } else {
                                return 6.8333f;
                            }
                        }
                    }
                } else {
                    return 6.7429f;
                }
            }
        }
    } else {
        if (features[2] <= 49.0250f) {
            if (features[2] <= 47.8750f) {
                if (features[2] <= 47.5400f) {
                    if (features[10] <= 11.2000f) {
                        if (features[2] <= 47.2000f) {
                            if (features[8] <= 3.1874f) {
                                return 6.8750f;
                            } else {
                                return 6.8083f;
                            }
                        } else {
                            return 6.8000f;
                        }
                    } else {
                        return 6.7000f;
                    }
                } else {
                    if (features[13] <= 47.8545f) {
                        if (features[5] <= 0.0010f) {
                            if (features[5] <= 0.0003f) {
                                if (features[10] <= 10.1500f) {
                                    return 6.7091f;
                                } else {
                                    return 6.7000f;
                                }
                            } else {
                                return 6.7571f;
                            }
                        } else {
                            return 6.6600f;
                        }
                    } else {
                        if (features[4] <= 0.0009f) {
                            return 6.7417f;
                        } else {
                            return 6.8000f;
                        }
                    }
                }
            } else {
                if (features[2] <= 48.5150f) {
                    if (features[4] <= 0.0226f) {
                        if (features[8] <= 4.1563f) {
                            if (features[8] <= 4.1361f) {
                                if (features[4] <= -0.0012f) {
                                    if (features[6] <= 2.8063f) {
                                        return 6.6333f;
                                    } else {
                                        return 6.6833f;
                                    }
                                } else {
                                    if (features[8] <= 3.1027f) {
                                        return 6.7000f;
                                    } else {
                                        return 6.6733f;
                                    }
                                }
                            } else {
                                return 6.6375f;
                            }
                        } else {
                            if (features[4] <= -0.0012f) {
                                return 6.7167f;
                            } else {
                                return 6.7000f;
                            }
                        }
                    } else {
                        return 6.6231f;
                    }
                } else {
                    if (features[8] <= 4.1076f) {
                        if (features[5] <= 0.0006f) {
                            if (features[2] <= 48.7450f) {
                                return 6.6000f;
                            } else {
                                return 6.6000f;
                            }
                        } else {
                            return 6.5778f;
                        }
                    } else {
                        return 6.6375f;
                    }
                }
            }
        } else {
            if (features[6] <= 2.6413f) {
                if (features[2] <= 49.9050f) {
                    if (features[4] <= -0.0018f) {
                        return 6.4500f;
                    } else {
                        if (features[2] <= 49.2450f) {
                            return 6.5571f;
                        } else {
                            if (features[5] <= 0.0005f) {
                                return 6.5000f;
                            } else {
                                return 6.4900f;
                            }
                        }
                    }
                } else {
                    if (features[2] <= 49.9450f) {
                        if (features[5] <= 0.0003f) {
                            if (features[5] <= 0.0002f) {
                                return 6.4429f;
                            } else {
                                return 6.4667f;
                            }
                        } else {
                            if (features[5] <= 0.0005f) {
                                return 6.4077f;
                            } else {
                                if (features[4] <= -0.0028f) {
                                    return 6.4333f;
                                } else {
                                    return 6.4571f;
                                }
                            }
                        }
                    } else {
                        if (features[8] <= 5.0015f) {
                            if (features[4] <= 0.0003f) {
                                if (features[8] <= 4.0020f) {
                                    if (features[5] <= 0.0003f) {
                                        return 6.4295f;
                                    } else {
                                        return 6.4000f;
                                    }
                                } else {
                                    if (features[8] <= 4.0028f) {
                                        return 6.4000f;
                                    } else {
                                        return 6.4130f;
                                    }
                                }
                            } else {
                                if (features[5] <= 0.0012f) {
                                    if (features[8] <= 3.0003f) {
                                        return 6.4000f;
                                    } else {
                                        return 6.4054f;
                                    }
                                } else {
                                    if (features[8] <= 3.0015f) {
                                        return 6.4071f;
                                    } else {
                                        return 6.4429f;
                                    }
                                }
                            }
                        } else {
                            if (features[2] <= 49.9650f) {
                                return 6.4176f;
                            } else {
                                if (features[2] <= 49.9750f) {
                                    return 6.4500f;
                                } else {
                                    if (features[5] <= 0.0001f) {
                                        return 6.4200f;
                                    } else {
                                        return 6.4500f;
                                    }
                                }
                            }
                        }
                    }
                }
            } else {
                if (features[2] <= 49.2850f) {
                    if (features[6] <= 2.8063f) {
                        return 6.5071f;
                    } else {
                        return 6.6000f;
                    }
                } else {
                    if (features[4] <= 0.1147f) {
                        if (features[2] <= 49.4450f) {
                            return 6.5417f;
                        } else {
                            if (features[7] <= 49.7852f) {
                                if (features[2] <= 49.6300f) {
                                    return 6.5067f;
                                } else {
                                    return 6.4333f;
                                }
                            } else {
                                return 6.5000f;
                            }
                        }
                    } else {
                        if (features[6] <= 2.9763f) {
                            if (features[4] <= 0.1626f) {
                                return 6.4125f;
                            } else {
                                return 6.4000f;
                            }
                        } else {
                            if (features[7] <= 47.6442f) {
                                return 6.4455f;
                            } else {
                                if (features[6] <= 3.5162f) {
                                    return 6.4444f;
                                } else {
                                    if (features[8] <= 3.5007f) {
                                        return 6.4667f;
                                    } else {
                                        return 6.5000f;
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

float predictETA_tree7(float features[14]) {
    if (features[2] <= 46.9450f) {
        if (features[2] <= 41.7950f) {
            if (features[2] <= 38.0600f) {
                if (features[2] <= 36.3250f) {
                    return 9.0833f;
                } else {
                    return 8.4250f;
                }
            } else {
                if (features[7] <= 37.0100f) {
                    return 8.1444f;
                } else {
                    if (features[2] <= 40.9300f) {
                        if (features[2] <= 40.1750f) {
                            return 7.8500f;
                        } else {
                            return 7.7900f;
                        }
                    } else {
                        return 7.6000f;
                    }
                }
            }
        } else {
            if (features[2] <= 45.2600f) {
                if (features[2] <= 43.4950f) {
                    if (features[2] <= 42.5550f) {
                        if (features[2] <= 42.2500f) {
                            return 7.4625f;
                        } else {
                            return 7.4000f;
                        }
                    } else {
                        return 7.3187f;
                    }
                } else {
                    if (features[11] <= 7.1500f) {
                        if (features[2] <= 45.1800f) {
                            return 7.2000f;
                        } else {
                            return 7.1000f;
                        }
                    } else {
                        if (features[4] <= 0.3049f) {
                            if (features[6] <= 5.1762f) {
                                if (features[4] <= 0.0003f) {
                                    return 7.1286f;
                                } else {
                                    if (features[8] <= 3.4134f) {
                                        return 7.1000f;
                                    } else {
                                        return 7.1000f;
                                    }
                                }
                            } else {
                                return 7.1571f;
                            }
                        } else {
                            return 7.0571f;
                        }
                    }
                }
            } else {
                if (features[2] <= 45.8800f) {
                    if (features[5] <= 5.2556f) {
                        if (features[2] <= 45.5550f) {
                            if (features[5] <= 0.0001f) {
                                return 7.1071f;
                            } else {
                                if (features[2] <= 45.4750f) {
                                    return 7.0857f;
                                } else {
                                    return 7.0200f;
                                }
                            }
                        } else {
                            if (features[11] <= 7.0500f) {
                                return 7.0667f;
                            } else {
                                if (features[2] <= 45.6700f) {
                                    return 7.0400f;
                                } else {
                                    return 7.0000f;
                                }
                            }
                        }
                    } else {
                        return 6.9111f;
                    }
                } else {
                    if (features[5] <= 6.3206f) {
                        if (features[2] <= 46.6450f) {
                            if (features[2] <= 46.1000f) {
                                if (features[4] <= 0.0014f) {
                                    if (features[4] <= -0.0009f) {
                                        return 7.0000f;
                                    } else {
                                        return 7.0167f;
                                    }
                                } else {
                                    return 6.9500f;
                                }
                            } else {
                                if (features[11] <= 6.9500f) {
                                    if (features[2] <= 46.5450f) {
                                        return 7.0000f;
                                    } else {
                                        return 6.9583f;
                                    }
                                } else {
                                    if (features[2] <= 46.3050f) {
                                        return 6.9548f;
                                    } else {
                                        return 6.9000f;
                                    }
                                }
                            }
                        } else {
                            if (features[2] <= 46.8000f) {
                                return 6.9000f;
                            } else {
                                if (features[7] <= 46.8363f) {
                                    return 6.8667f;
                                } else {
                                    return 6.9000f;
                                }
                            }
                        }
                    } else {
                        return 6.8100f;
                    }
                }
            }
        }
    } else {
        if (features[2] <= 49.0650f) {
            if (features[2] <= 47.8750f) {
                if (features[11] <= 6.9500f) {
                    if (features[2] <= 47.1900f) {
                        if (features[7] <= 47.0084f) {
                            if (features[4] <= 0.0006f) {
                                return 6.8100f;
                            } else {
                                return 6.8333f;
                            }
                        } else {
                            return 6.9000f;
                        }
                    } else {
                        if (features[2] <= 47.7250f) {
                            if (features[2] <= 47.5900f) {
                                return 6.8000f;
                            } else {
                                if (features[7] <= 47.6422f) {
                                    return 6.7500f;
                                } else {
                                    return 6.8000f;
                                }
                            }
                        } else {
                            if (features[4] <= 0.0009f) {
                                if (features[9] <= 1.8783f) {
                                    return 6.7429f;
                                } else {
                                    return 6.7000f;
                                }
                            } else {
                                return 6.7778f;
                            }
                        }
                    }
                } else {
                    return 6.6154f;
                }
            } else {
                if (features[2] <= 48.5150f) {
                    if (features[8] <= 3.1204f) {
                        if (features[4] <= 0.0009f) {
                            if (features[8] <= 3.1040f) {
                                if (features[8] <= 2.0736f) {
                                    return 6.6833f;
                                } else {
                                    return 6.7000f;
                                }
                            } else {
                                return 6.6444f;
                            }
                        } else {
                            return 6.6385f;
                        }
                    } else {
                        if (features[2] <= 48.3400f) {
                            if (features[5] <= 0.0009f) {
                                if (features[7] <= 47.8194f) {
                                    return 6.7000f;
                                } else {
                                    return 6.7000f;
                                }
                            } else {
                                return 6.7111f;
                            }
                        } else {
                            return 6.6750f;
                        }
                    }
                } else {
                    if (features[7] <= 48.2993f) {
                        return 6.5667f;
                    } else {
                        if (features[8] <= 4.1080f) {
                            return 6.6000f;
                        } else {
                            return 6.6222f;
                        }
                    }
                }
            }
        } else {
            if (features[6] <= 2.6413f) {
                if (features[2] <= 49.8850f) {
                    if (features[2] <= 49.2100f) {
                        return 6.5833f;
                    } else {
                        if (features[4] <= -0.0015f) {
                            return 6.4400f;
                        } else {
                            return 6.5000f;
                        }
                    }
                } else {
                    if (features[8] <= 5.0055f) {
                        if (features[2] <= 49.9850f) {
                            if (features[4] <= 0.0028f) {
                                if (features[8] <= 2.0022f) {
                                    return 6.4000f;
                                } else {
                                    if (features[8] <= 5.0045f) {
                                        return 6.4185f;
                                    } else {
                                        return 6.4000f;
                                    }
                                }
                            } else {
                                if (features[2] <= 49.9750f) {
                                    if (features[5] <= 0.0011f) {
                                        return 6.4667f;
                                    } else {
                                        return 6.4500f;
                                    }
                                } else {
                                    return 6.4100f;
                                }
                            }
                        } else {
                            if (features[4] <= 0.0009f) {
                                return 6.4000f;
                            } else {
                                if (features[5] <= 0.0002f) {
                                    return 6.4222f;
                                } else {
                                    if (features[5] <= 0.0008f) {
                                        return 6.4000f;
                                    } else {
                                        return 6.4077f;
                                    }
                                }
                            }
                        }
                    } else {
                        return 6.4467f;
                    }
                }
            } else {
                if (features[4] <= 0.0743f) {
                    if (features[2] <= 49.4450f) {
                        if (features[11] <= 6.5500f) {
                            if (features[5] <= 0.0001f) {
                                return 6.6000f;
                            } else {
                                return 6.5667f;
                            }
                        } else {
                            return 6.5000f;
                        }
                    } else {
                        if (features[11] <= 6.4500f) {
                            return 6.5000f;
                        } else {
                            if (features[2] <= 49.6650f) {
                                return 6.5000f;
                            } else {
                                return 6.4667f;
                            }
                        }
                    }
                } else {
                    if (features[13] <= 50.0805f) {
                        if (features[6] <= 2.9763f) {
                            return 6.4000f;
                        } else {
                            if (features[5] <= 5.7601f) {
                                if (features[2] <= 49.7350f) {
                                    return 6.5250f;
                                } else {
                                    return 6.4692f;
                                }
                            } else {
                                if (features[4] <= 0.3620f) {
                                    return 6.4143f;
                                } else {
                                    if (features[8] <= 4.0020f) {
                                        return 6.5000f;
                                    } else {
                                        return 6.4571f;
                                    }
                                }
                            }
                        }
                    } else {
                        return 6.5000f;
                    }
                }
            }
        }
    }
}

float predictETA_tree8(float features[14]) {
    if (features[2] <= 47.1850f) {
        if (features[2] <= 42.9600f) {
            if (features[11] <= 8.5500f) {
                if (features[2] <= 41.0000f) {
                    if (features[2] <= 40.1050f) {
                        return 7.9125f;
                    } else {
                        return 7.7750f;
                    }
                } else {
                    if (features[2] <= 42.0550f) {
                        if (features[2] <= 41.5750f) {
                            return 7.6000f;
                        } else {
                            return 7.5063f;
                        }
                    } else {
                        if (features[5] <= 5.9439f) {
                            return 7.4000f;
                        } else {
                            return 7.3714f;
                        }
                    }
                }
            } else {
                return 8.6200f;
            }
        } else {
            if (features[2] <= 46.0950f) {
                if (features[2] <= 45.4050f) {
                    if (features[11] <= 7.5500f) {
                        if (features[4] <= 0.2936f) {
                            if (features[6] <= 3.3312f) {
                                if (features[8] <= 5.5109f) {
                                    return 7.1000f;
                                } else {
                                    return 7.1429f;
                                }
                            } else {
                                if (features[8] <= 3.3208f) {
                                    return 7.1333f;
                                } else {
                                    return 7.1778f;
                                }
                            }
                        } else {
                            return 7.0467f;
                        }
                    } else {
                        return 7.2556f;
                    }
                } else {
                    if (features[4] <= 0.2947f) {
                        if (features[2] <= 45.8450f) {
                            if (features[13] <= 45.8179f) {
                                if (features[2] <= 45.6700f) {
                                    if (features[10] <= 10.6500f) {
                                        return 7.0700f;
                                    } else {
                                        return 7.0188f;
                                    }
                                } else {
                                    if (features[5] <= 0.0002f) {
                                        return 7.0200f;
                                    } else {
                                        return 7.0000f;
                                    }
                                }
                            } else {
                                return 7.1000f;
                            }
                        } else {
                            return 7.0000f;
                        }
                    } else {
                        if (features[7] <= 43.0049f) {
                            return 6.8714f;
                        } else {
                            return 6.9400f;
                        }
                    }
                }
            } else {
                if (features[2] <= 46.5650f) {
                    if (features[5] <= 0.4624f) {
                        if (features[2] <= 46.3050f) {
                            if (features[8] <= 3.2425f) {
                                return 6.9882f;
                            } else {
                                if (features[5] <= 0.0001f) {
                                    return 6.9000f;
                                } else {
                                    return 6.9778f;
                                }
                            }
                        } else {
                            if (features[13] <= 46.4772f) {
                                return 6.9000f;
                            } else {
                                return 6.9636f;
                            }
                        }
                    } else {
                        return 6.8333f;
                    }
                } else {
                    if (features[12] <= 43.1324f) {
                        return 6.7167f;
                    } else {
                        if (features[8] <= 4.2608f) {
                            if (features[8] <= 3.1878f) {
                                if (features[5] <= 0.0002f) {
                                    return 6.9000f;
                                } else {
                                    return 6.8667f;
                                }
                            } else {
                                if (features[10] <= 10.3500f) {
                                    return 6.8067f;
                                } else {
                                    return 6.8533f;
                                }
                            }
                        } else {
                            if (features[4] <= 0.0015f) {
                                return 6.9000f;
                            } else {
                                return 6.8800f;
                            }
                        }
                    }
                }
            }
        }
    } else {
        if (features[2] <= 49.1200f) {
            if (features[2] <= 48.0750f) {
                if (features[10] <= 11.0500f) {
                    if (features[2] <= 47.5400f) {
                        return 6.8000f;
                    } else {
                        if (features[2] <= 47.8450f) {
                            if (features[7] <= 47.8194f) {
                                if (features[2] <= 47.6650f) {
                                    return 6.7455f;
                                } else {
                                    return 6.7118f;
                                }
                            } else {
                                return 6.7850f;
                            }
                        } else {
                            if (features[5] <= 0.0007f) {
                                if (features[1] <= 125.0000f) {
                                    return 6.7000f;
                                } else {
                                    return 6.7000f;
                                }
                            } else {
                                return 6.7250f;
                            }
                        }
                    }
                } else {
                    return 6.6222f;
                }
            } else {
                if (features[2] <= 48.4900f) {
                    if (features[7] <= 48.0572f) {
                        return 6.6000f;
                    } else {
                        if (features[8] <= 4.1472f) {
                            if (features[5] <= 0.0002f) {
                                if (features[5] <= 0.0000f) {
                                    return 6.6250f;
                                } else {
                                    return 6.6556f;
                                }
                            } else {
                                if (features[8] <= 3.1018f) {
                                    return 6.6625f;
                                } else {
                                    return 6.6923f;
                                }
                            }
                        } else {
                            if (features[8] <= 5.1771f) {
                                return 6.7000f;
                            } else {
                                return 6.6857f;
                            }
                        }
                    }
                } else {
                    if (features[4] <= 0.0006f) {
                        if (features[5] <= 0.0001f) {
                            return 6.6400f;
                        } else {
                            if (features[5] <= 0.0002f) {
                                return 6.6000f;
                            } else {
                                return 6.6000f;
                            }
                        }
                    } else {
                        if (features[9] <= 2.6833f) {
                            if (features[8] <= 3.0918f) {
                                return 6.6000f;
                            } else {
                                return 6.5882f;
                            }
                        } else {
                            return 6.5667f;
                        }
                    }
                }
            }
        } else {
            if (features[6] <= 2.6413f) {
                if (features[2] <= 49.9050f) {
                    if (features[4] <= -0.0015f) {
                        return 6.4250f;
                    } else {
                        if (features[2] <= 49.2950f) {
                            return 6.5125f;
                        } else {
                            return 6.5000f;
                        }
                    }
                } else {
                    if (features[8] <= 4.0044f) {
                        if (features[5] <= 0.0000f) {
                            if (features[2] <= 49.9700f) {
                                if (features[5] <= 0.0000f) {
                                    return 6.4429f;
                                } else {
                                    if (features[9] <= 1.8783f) {
                                        return 6.4333f;
                                    } else {
                                        return 6.4125f;
                                    }
                                }
                            } else {
                                return 6.4000f;
                            }
                        } else {
                            if (features[8] <= 4.0012f) {
                                if (features[8] <= 3.0015f) {
                                    if (features[5] <= 0.0009f) {
                                        return 6.4029f;
                                    } else {
                                        return 6.4167f;
                                    }
                                } else {
                                    if (features[4] <= 0.0022f) {
                                        return 6.4190f;
                                    } else {
                                        return 6.4000f;
                                    }
                                }
                            } else {
                                return 6.4000f;
                            }
                        }
                    } else {
                        if (features[4] <= -0.0022f) {
                            if (features[4] <= -0.0034f) {
                                return 6.4400f;
                            } else {
                                return 6.4875f;
                            }
                        } else {
                            if (features[4] <= 0.0015f) {
                                if (features[8] <= 5.0065f) {
                                    if (features[2] <= 49.9550f) {
                                        return 6.4111f;
                                    } else {
                                        return 6.4279f;
                                    }
                                } else {
                                    return 6.4429f;
                                }
                            } else {
                                return 6.4077f;
                            }
                        }
                    }
                }
            } else {
                if (features[2] <= 49.2850f) {
                    if (features[6] <= 2.8063f) {
                        return 6.5000f;
                    } else {
                        return 6.6000f;
                    }
                } else {
                    if (features[5] <= 0.7818f) {
                        if (features[2] <= 49.5200f) {
                            if (features[8] <= 3.5392f) {
                                return 6.5571f;
                            } else {
                                return 6.5000f;
                            }
                        } else {
                            if (features[7] <= 49.7852f) {
                                if (features[2] <= 49.6200f) {
                                    return 6.5000f;
                                } else {
                                    return 6.4556f;
                                }
                            } else {
                                return 6.5000f;
                            }
                        }
                    } else {
                        if (features[6] <= 3.1513f) {
                            if (features[8] <= 3.0015f) {
                                return 6.4375f;
                            } else {
                                return 6.4000f;
                            }
                        } else {
                            if (features[7] <= 47.6442f) {
                                return 6.4111f;
                            } else {
                                if (features[5] <= 6.7187f) {
                                    if (features[2] <= 49.9850f) {
                                        return 6.4636f;
                                    } else {
                                        return 6.5000f;
                                    }
                                } else {
                                    return 6.4444f;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

float predictETA_tree9(float features[14]) {
    if (features[2] <= 46.7050f) {
        if (features[2] <= 41.7950f) {
            if (features[2] <= 38.0600f) {
                return 8.7818f;
            } else {
                if (features[2] <= 40.0250f) {
                    return 8.0538f;
                } else {
                    if (features[2] <= 41.0450f) {
                        if (features[2] <= 40.5100f) {
                            return 7.8000f;
                        } else {
                            return 7.7250f;
                        }
                    } else {
                        return 7.5778f;
                    }
                }
            }
        } else {
            if (features[2] <= 45.4050f) {
                if (features[2] <= 43.5350f) {
                    if (features[2] <= 42.9600f) {
                        if (features[4] <= 0.2737f) {
                            return 7.4571f;
                        } else {
                            return 7.4000f;
                        }
                    } else {
                        return 7.3000f;
                    }
                } else {
                    if (features[4] <= 0.3213f) {
                        if (features[2] <= 45.1350f) {
                            if (features[13] <= 45.1770f) {
                                if (features[7] <= 41.6582f) {
                                    return 7.1875f;
                                } else {
                                    if (features[4] <= 0.0006f) {
                                        return 7.1571f;
                                    } else {
                                        return 7.1000f;
                                    }
                                }
                            } else {
                                if (features[8] <= 3.3264f) {
                                    return 7.2000f;
                                } else {
                                    return 7.2000f;
                                }
                            }
                        } else {
                            if (features[7] <= 45.1471f) {
                                return 7.0917f;
                            } else {
                                if (features[7] <= 45.3590f) {
                                    return 7.1600f;
                                } else {
                                    return 7.1000f;
                                }
                            }
                        }
                    } else {
                        return 7.0111f;
                    }
                }
            } else {
                if (features[4] <= 0.3416f) {
                    if (features[2] <= 45.9400f) {
                        if (features[4] <= 0.2947f) {
                            if (features[2] <= 45.8650f) {
                                if (features[11] <= 7.0500f) {
                                    if (features[4] <= 0.0003f) {
                                        return 7.0857f;
                                    } else {
                                        return 7.1000f;
                                    }
                                } else {
                                    if (features[2] <= 45.6750f) {
                                        return 7.0545f;
                                    } else {
                                        return 7.0000f;
                                    }
                                }
                            } else {
                                return 7.0000f;
                            }
                        } else {
                            return 6.9250f;
                        }
                    } else {
                        if (features[2] <= 46.3300f) {
                            if (features[7] <= 46.2249f) {
                                if (features[8] <= 4.3436f) {
                                    if (features[2] <= 46.1100f) {
                                        return 7.0000f;
                                    } else {
                                        return 6.9520f;
                                    }
                                } else {
                                    return 6.9273f;
                                }
                            } else {
                                return 7.0000f;
                            }
                        } else {
                            if (features[11] <= 6.9500f) {
                                if (features[2] <= 46.6200f) {
                                    return 6.9818f;
                                } else {
                                    return 6.9000f;
                                }
                            } else {
                                if (features[5] <= 0.0001f) {
                                    return 6.9000f;
                                } else {
                                    return 6.9000f;
                                }
                            }
                        }
                    }
                } else {
                    return 6.7941f;
                }
            }
        }
    } else {
        if (features[2] <= 48.9650f) {
            if (features[2] <= 47.8350f) {
                if (features[5] <= 6.5513f) {
                    if (features[2] <= 47.0050f) {
                        if (features[6] <= 3.1513f) {
                            if (features[8] <= 3.1928f) {
                                return 6.9000f;
                            } else {
                                if (features[6] <= 2.9763f) {
                                    return 6.8143f;
                                } else {
                                    return 6.8625f;
                                }
                            }
                        } else {
                            return 6.9000f;
                        }
                    } else {
                        if (features[2] <= 47.5450f) {
                            if (features[2] <= 47.1900f) {
                                if (features[6] <= 2.9763f) {
                                    return 6.8000f;
                                } else {
                                    return 6.8600f;
                                }
                            } else {
                                return 6.8000f;
                            }
                        } else {
                            if (features[11] <= 6.7500f) {
                                return 6.8000f;
                            } else {
                                if (features[5] <= 0.0001f) {
                                    return 6.7167f;
                                } else {
                                    return 6.7500f;
                                }
                            }
                        }
                    }
                } else {
                    return 6.6500f;
                }
            } else {
                if (features[2] <= 48.5150f) {
                    if (features[8] <= 3.1204f) {
                        if (features[7] <= 47.9967f) {
                            return 6.6273f;
                        } else {
                            if (features[2] <= 48.3800f) {
                                if (features[8] <= 3.1033f) {
                                    return 6.7000f;
                                } else {
                                    if (features[4] <= -0.0009f) {
                                        return 6.6778f;
                                    } else {
                                        return 6.6500f;
                                    }
                                }
                            } else {
                                return 6.6400f;
                            }
                        }
                    } else {
                        if (features[2] <= 48.2350f) {
                            if (features[5] <= 0.0016f) {
                                if (features[2] <= 47.9050f) {
                                    return 6.7300f;
                                } else {
                                    if (features[5] <= 0.0005f) {
                                        return 6.7000f;
                                    } else {
                                        return 6.7083f;
                                    }
                                }
                            } else {
                                return 6.6818f;
                            }
                        } else {
                            if (features[7] <= 48.2344f) {
                                return 6.6429f;
                            } else {
                                if (features[8] <= 5.1573f) {
                                    return 6.6857f;
                                } else {
                                    return 6.7000f;
                                }
                            }
                        }
                    }
                } else {
                    if (features[8] <= 5.1314f) {
                        return 6.6000f;
                    } else {
                        return 6.6333f;
                    }
                }
            }
        } else {
            if (features[6] <= 2.6413f) {
                if (features[2] <= 49.9050f) {
                    if (features[4] <= -0.0015f) {
                        return 6.4333f;
                    } else {
                        if (features[2] <= 49.3250f) {
                            return 6.5333f;
                        } else {
                            return 6.5000f;
                        }
                    }
                } else {
                    if (features[2] <= 49.9650f) {
                        if (features[8] <= 2.5030f) {
                            if (features[5] <= 0.0001f) {
                                return 6.4077f;
                            } else {
                                return 6.4000f;
                            }
                        } else {
                            if (features[4] <= -0.0022f) {
                                if (features[4] <= -0.0028f) {
                                    return 6.4417f;
                                } else {
                                    return 6.4700f;
                                }
                            } else {
                                if (features[5] <= 0.0000f) {
                                    if (features[8] <= 4.5040f) {
                                        return 6.4538f;
                                    } else {
                                        return 6.4000f;
                                    }
                                } else {
                                    if (features[9] <= 1.4490f) {
                                        return 6.4273f;
                                    } else {
                                        return 6.4074f;
                                    }
                                }
                            }
                        }
                    } else {
                        if (features[5] <= 0.0008f) {
                            if (features[5] <= 0.0002f) {
                                if (features[4] <= 0.0009f) {
                                    if (features[8] <= 4.5017f) {
                                        return 6.4028f;
                                    } else {
                                        return 6.4148f;
                                    }
                                } else {
                                    if (features[8] <= 4.0012f) {
                                        return 6.4364f;
                                    } else {
                                        return 6.4000f;
                                    }
                                }
                            } else {
                                return 6.4000f;
                            }
                        } else {
                            if (features[4] <= 0.0046f) {
                                return 6.4600f;
                            } else {
                                if (features[8] <= 4.0004f) {
                                    if (features[4] <= 0.0318f) {
                                        return 6.4000f;
                                    } else {
                                        return 6.4000f;
                                    }
                                } else {
                                    return 6.4143f;
                                }
                            }
                        }
                    }
                }
            } else {
                if (features[2] <= 49.2950f) {
                    if (features[13] <= 49.3158f) {
                        if (features[2] <= 49.0750f) {
                            if (features[5] <= 0.0003f) {
                                return 6.5778f;
                            } else {
                                return 6.5417f;
                            }
                        } else {
                            return 6.4933f;
                        }
                    } else {
                        return 6.6000f;
                    }
                } else {
                    if (features[7] <= 49.4127f) {
                        if (features[10] <= 10.0500f) {
                            return 6.4143f;
                        } else {
                            if (features[5] <= 5.7786f) {
                                return 6.5000f;
                            } else {
                                if (features[10] <= 10.7000f) {
                                    if (features[6] <= 3.9013f) {
                                        return 6.4167f;
                                    } else {
                                        return 6.4400f;
                                    }
                                } else {
                                    return 6.4875f;
                                }
                            }
                        }
                    } else {
                        if (features[2] <= 49.5250f) {
                            return 6.5308f;
                        } else {
                            if (features[11] <= 6.4500f) {
                                return 6.5000f;
                            } else {
                                if (features[2] <= 49.6650f) {
                                    return 6.5000f;
                                } else {
                                    return 6.4571f;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

float predictETA(float features[14]) {
    float sum = 0.0f;
    sum += predictETA_tree0(features);
    sum += predictETA_tree1(features);
    sum += predictETA_tree2(features);
    sum += predictETA_tree3(features);
    sum += predictETA_tree4(features);
    sum += predictETA_tree5(features);
    sum += predictETA_tree6(features);
    sum += predictETA_tree7(features);
    sum += predictETA_tree8(features);
    sum += predictETA_tree9(features);
    return sum / 10.0f;
}


/*
 * PREDICTETD Prediction Model
 * Auto-generated from random forest (5 trees)
 * 
 * Feature indices:
 * [0] distance_remaining\n * [1] train_length\n * [2] last_speed\n * [3] last_accel\n * [4] speed_trend\n * [5] speed_variance\n * [6] time_variance\n * [7] avg_speed_overall\n * [8] length_speed_ratio\n * [9] distance_length_ratio\n * [10] dt_interval_0\n * [11] dt_interval_1\n * [12] avg_speed_0\n * [13] avg_speed_1
 */

float predictETD_tree0(float features[14]) {
    if (features[8] <= 3.2489f) {
        if (features[8] <= 2.1480f) {
            if (features[8] <= 2.0549f) {
                if (features[2] <= 49.6450f) {
                    if (features[8] <= 2.0305f) {
                        if (features[7] <= 49.4661f) {
                            return 8.5000f;
                        } else {
                            return 8.5889f;
                        }
                    } else {
                        if (features[8] <= 2.0419f) {
                            return 8.6000f;
                        } else {
                            return 8.6222f;
                        }
                    }
                } else {
                    if (features[11] <= 6.4500f) {
                        return 8.5000f;
                    } else {
                        if (features[5] <= 1.3428f) {
                            if (features[5] <= 0.0007f) {
                                if (features[2] <= 49.9250f) {
                                    return 8.4286f;
                                } else {
                                    if (features[5] <= 0.0002f) {
                                        return 8.4047f;
                                    } else {
                                        return 8.4000f;
                                    }
                                }
                            } else {
                                if (features[4] <= 0.0046f) {
                                    return 8.4667f;
                                } else {
                                    return 8.4000f;
                                }
                            }
                        } else {
                            return 8.4600f;
                        }
                    }
                }
            } else {
                if (features[2] <= 47.5400f) {
                    if (features[5] <= 0.0008f) {
                        if (features[8] <= 2.1227f) {
                            return 8.9000f;
                        } else {
                            return 9.0056f;
                        }
                    } else {
                        return 8.8167f;
                    }
                } else {
                    if (features[2] <= 48.2250f) {
                        if (features[8] <= 2.0890f) {
                            return 8.7600f;
                        } else {
                            return 8.8100f;
                        }
                    } else {
                        return 8.7000f;
                    }
                }
            }
        } else {
            if (features[8] <= 3.1005f) {
                if (features[2] <= 40.9600f) {
                    return 10.5750f;
                } else {
                    if (features[8] <= 2.3035f) {
                        if (features[2] <= 45.8150f) {
                            if (features[4] <= 0.2713f) {
                                if (features[8] <= 2.2119f) {
                                    return 9.2917f;
                                } else {
                                    if (features[5] <= 0.0002f) {
                                        return 9.4000f;
                                    } else {
                                        return 9.3286f;
                                    }
                                }
                            } else {
                                return 9.2000f;
                            }
                        } else {
                            if (features[7] <= 46.0577f) {
                                return 9.2000f;
                            } else {
                                if (features[2] <= 46.2650f) {
                                    return 9.1375f;
                                } else {
                                    return 9.1000f;
                                }
                            }
                        }
                    } else {
                        if (features[2] <= 49.6250f) {
                            if (features[2] <= 48.4550f) {
                                return 9.7667f;
                            } else {
                                if (features[8] <= 3.0631f) {
                                    if (features[13] <= 49.3158f) {
                                        return 9.5636f;
                                    } else {
                                        return 9.6000f;
                                    }
                                } else {
                                    return 9.6545f;
                                }
                            }
                        } else {
                            if (features[13] <= 50.0805f) {
                                if (features[8] <= 3.0063f) {
                                    if (features[4] <= -0.0015f) {
                                        return 9.4467f;
                                    } else {
                                        return 9.4133f;
                                    }
                                } else {
                                    return 9.5000f;
                                }
                            } else {
                                if (features[4] <= -0.0019f) {
                                    return 9.5000f;
                                } else {
                                    return 9.5000f;
                                }
                            }
                        }
                    }
                }
            } else {
                if (features[8] <= 3.1649f) {
                    if (features[10] <= 10.1500f) {
                        if (features[8] <= 3.1276f) {
                            if (features[8] <= 3.1091f) {
                                return 9.7800f;
                            } else {
                                return 9.8000f;
                            }
                        } else {
                            return 9.8333f;
                        }
                    } else {
                        if (features[8] <= 3.1546f) {
                            return 9.9000f;
                        } else {
                            return 9.9429f;
                        }
                    }
                } else {
                    if (features[8] <= 3.2123f) {
                        if (features[5] <= 0.0002f) {
                            return 10.0300f;
                        } else {
                            return 10.0000f;
                        }
                    } else {
                        if (features[2] <= 46.4400f) {
                            return 10.1750f;
                        } else {
                            return 10.1000f;
                        }
                    }
                }
            }
        }
    } else {
        if (features[8] <= 4.3094f) {
            if (features[8] <= 4.1157f) {
                if (features[6] <= 5.7625f) {
                    if (features[8] <= 4.0352f) {
                        if (features[8] <= 3.3062f) {
                            if (features[8] <= 3.2758f) {
                                return 10.3000f;
                            } else {
                                return 10.3308f;
                            }
                        } else {
                            if (features[6] <= 2.6413f) {
                                if (features[2] <= 49.9550f) {
                                    if (features[5] <= 0.0004f) {
                                        return 10.4615f;
                                    } else {
                                        return 10.4250f;
                                    }
                                } else {
                                    if (features[5] <= 0.0002f) {
                                        return 10.4167f;
                                    } else {
                                        return 10.4000f;
                                    }
                                }
                            } else {
                                if (features[8] <= 3.4720f) {
                                    return 10.4071f;
                                } else {
                                    if (features[2] <= 49.9350f) {
                                        return 10.6125f;
                                    } else {
                                        return 10.4933f;
                                    }
                                }
                            }
                        }
                    } else {
                        if (features[2] <= 49.1250f) {
                            return 10.7000f;
                        } else {
                            return 10.5800f;
                        }
                    }
                } else {
                    return 11.2143f;
                }
            } else {
                if (features[2] <= 47.0050f) {
                    if (features[4] <= 0.0003f) {
                        return 11.1500f;
                    } else {
                        return 11.0857f;
                    }
                } else {
                    if (features[13] <= 47.1558f) {
                        return 10.7167f;
                    } else {
                        if (features[2] <= 48.0150f) {
                            if (features[2] <= 47.6650f) {
                                return 11.0000f;
                            } else {
                                if (features[4] <= 0.0003f) {
                                    return 10.9000f;
                                } else {
                                    return 10.9375f;
                                }
                            }
                        } else {
                            if (features[2] <= 48.2350f) {
                                return 10.8429f;
                            } else {
                                return 10.8000f;
                            }
                        }
                    }
                }
            }
        } else {
            if (features[8] <= 5.1768f) {
                if (features[11] <= 7.8500f) {
                    if (features[8] <= 5.0849f) {
                        if (features[8] <= 4.4082f) {
                            if (features[7] <= 44.3729f) {
                                return 11.0100f;
                            } else {
                                if (features[2] <= 46.1750f) {
                                    if (features[2] <= 45.8250f) {
                                        return 11.4333f;
                                    } else {
                                        return 11.3900f;
                                    }
                                } else {
                                    return 11.2600f;
                                }
                            }
                        } else {
                            if (features[7] <= 41.8886f) {
                                return 11.6833f;
                            } else {
                                if (features[6] <= 2.6413f) {
                                    if (features[8] <= 5.0085f) {
                                        return 11.4238f;
                                    } else {
                                        return 11.5200f;
                                    }
                                } else {
                                    if (features[4] <= 0.1221f) {
                                        return 11.5169f;
                                    } else {
                                        return 11.4333f;
                                    }
                                }
                            }
                        }
                    } else {
                        if (features[2] <= 48.6050f) {
                            return 11.8182f;
                        } else {
                            return 11.7167f;
                        }
                    }
                } else {
                    return 12.2167f;
                }
            } else {
                if (features[10] <= 12.5500f) {
                    if (features[2] <= 45.8000f) {
                        if (features[8] <= 5.5006f) {
                            if (features[4] <= 0.0020f) {
                                return 12.5286f;
                            } else {
                                return 12.4286f;
                            }
                        } else {
                            if (features[7] <= 44.9892f) {
                                return 12.5700f;
                            } else {
                                if (features[5] <= 0.0002f) {
                                    return 12.6857f;
                                } else {
                                    return 12.6286f;
                                }
                            }
                        }
                    } else {
                        if (features[8] <= 5.2737f) {
                            if (features[8] <= 5.2279f) {
                                if (features[4] <= -0.0003f) {
                                    return 11.8833f;
                                } else {
                                    return 11.8375f;
                                }
                            } else {
                                return 11.9933f;
                            }
                        } else {
                            if (features[8] <= 5.3277f) {
                                if (features[4] <= 0.0015f) {
                                    return 12.1000f;
                                } else {
                                    return 12.0900f;
                                }
                            } else {
                                if (features[5] <= 3.9005f) {
                                    if (features[12] <= 46.4125f) {
                                        return 12.4077f;
                                    } else {
                                        return 12.2455f;
                                    }
                                } else {
                                    return 12.0375f;
                                }
                            }
                        }
                    }
                } else {
                    if (features[8] <= 6.2005f) {
                        return 13.1071f;
                    } else {
                        return 14.0111f;
                    }
                }
            }
        }
    }
}

float predictETD_tree1(float features[14]) {
    if (features[8] <= 3.2595f) {
        if (features[8] <= 2.1542f) {
            if (features[2] <= 48.6250f) {
                if (features[8] <= 2.1182f) {
                    if (features[2] <= 48.2600f) {
                        if (features[4] <= 0.0006f) {
                            if (features[8] <= 2.1015f) {
                                return 8.8077f;
                            } else {
                                return 8.9000f;
                            }
                        } else {
                            return 8.7000f;
                        }
                    } else {
                        return 8.7000f;
                    }
                } else {
                    if (features[8] <= 2.1434f) {
                        return 8.9938f;
                    } else {
                        return 8.8111f;
                    }
                }
            } else {
                if (features[2] <= 49.2650f) {
                    if (features[4] <= -0.0009f) {
                        return 8.6294f;
                    } else {
                        if (features[4] <= 0.0024f) {
                            return 8.6000f;
                        } else {
                            return 8.5714f;
                        }
                    }
                } else {
                    if (features[6] <= 2.6413f) {
                        if (features[2] <= 49.8350f) {
                            return 8.5071f;
                        } else {
                            if (features[5] <= 0.0007f) {
                                if (features[5] <= 0.0000f) {
                                    return 8.4400f;
                                } else {
                                    if (features[5] <= 0.0002f) {
                                        return 8.4129f;
                                    } else {
                                        return 8.4000f;
                                    }
                                }
                            } else {
                                return 8.4571f;
                            }
                        }
                    } else {
                        if (features[5] <= 1.2331f) {
                            if (features[8] <= 2.0178f) {
                                if (features[2] <= 49.9350f) {
                                    return 8.4714f;
                                } else {
                                    return 8.5000f;
                                }
                            } else {
                                return 8.5667f;
                            }
                        } else {
                            if (features[4] <= 0.2883f) {
                                return 8.4286f;
                            } else {
                                return 8.4667f;
                            }
                        }
                    }
                }
            }
        } else {
            if (features[8] <= 3.0154f) {
                if (features[2] <= 40.9600f) {
                    return 10.6143f;
                } else {
                    if (features[8] <= 2.2886f) {
                        if (features[2] <= 45.8200f) {
                            if (features[5] <= 0.1324f) {
                                if (features[10] <= 10.7500f) {
                                    return 9.2867f;
                                } else {
                                    return 9.3692f;
                                }
                            } else {
                                return 9.1700f;
                            }
                        } else {
                            if (features[8] <= 2.1690f) {
                                return 9.1091f;
                            } else {
                                return 9.2000f;
                            }
                        }
                    } else {
                        if (features[2] <= 49.7900f) {
                            return 9.6286f;
                        } else {
                            if (features[13] <= 50.0805f) {
                                if (features[2] <= 49.9250f) {
                                    return 9.4667f;
                                } else {
                                    if (features[5] <= 0.0004f) {
                                        return 9.4070f;
                                    } else {
                                        return 9.4333f;
                                    }
                                }
                            } else {
                                return 9.5000f;
                            }
                        }
                    }
                }
            } else {
                if (features[2] <= 47.7700f) {
                    if (features[2] <= 46.2800f) {
                        return 10.4714f;
                    } else {
                        if (features[5] <= 1.2457f) {
                            if (features[8] <= 3.1966f) {
                                if (features[2] <= 47.4450f) {
                                    return 10.0000f;
                                } else {
                                    return 9.9182f;
                                }
                            } else {
                                if (features[8] <= 3.2210f) {
                                    if (features[6] <= 2.9763f) {
                                        return 10.1000f;
                                    } else {
                                        return 10.0556f;
                                    }
                                } else {
                                    return 10.1714f;
                                }
                            }
                        } else {
                            return 9.7857f;
                        }
                    }
                } else {
                    if (features[8] <= 3.0766f) {
                        if (features[2] <= 49.4700f) {
                            return 9.5875f;
                        } else {
                            return 9.5250f;
                        }
                    } else {
                        if (features[8] <= 3.1082f) {
                            if (features[8] <= 3.0931f) {
                                return 9.7000f;
                            } else {
                                return 9.7429f;
                            }
                        } else {
                            if (features[2] <= 48.0300f) {
                                return 9.8375f;
                            } else {
                                return 9.7900f;
                            }
                        }
                    }
                }
            }
        }
    } else {
        if (features[8] <= 4.3192f) {
            if (features[8] <= 4.1148f) {
                if (features[13] <= 40.3813f) {
                    return 11.3727f;
                } else {
                    if (features[8] <= 4.0384f) {
                        if (features[11] <= 7.6500f) {
                            if (features[8] <= 3.3043f) {
                                if (features[5] <= 0.0007f) {
                                    return 10.3286f;
                                } else {
                                    return 10.2333f;
                                }
                            } else {
                                if (features[7] <= 49.9127f) {
                                    if (features[8] <= 4.0044f) {
                                        return 10.4070f;
                                    } else {
                                        return 10.4842f;
                                    }
                                } else {
                                    if (features[8] <= 4.0012f) {
                                        return 10.5000f;
                                    } else {
                                        return 10.5000f;
                                    }
                                }
                            }
                        } else {
                            return 10.7667f;
                        }
                    } else {
                        if (features[8] <= 4.0833f) {
                            return 10.6500f;
                        } else {
                            return 10.7000f;
                        }
                    }
                }
            } else {
                if (features[2] <= 47.2050f) {
                    if (features[10] <= 11.2500f) {
                        if (features[2] <= 46.9400f) {
                            if (features[4] <= 0.0009f) {
                                return 11.2000f;
                            } else {
                                return 11.1600f;
                            }
                        } else {
                            return 11.1000f;
                        }
                    } else {
                        return 10.8286f;
                    }
                } else {
                    if (features[2] <= 48.1550f) {
                        if (features[8] <= 4.1977f) {
                            if (features[6] <= 2.9763f) {
                                return 10.9000f;
                            } else {
                                return 10.9500f;
                            }
                        } else {
                            return 10.7800f;
                        }
                    } else {
                        return 10.8000f;
                    }
                }
            }
        } else {
            if (features[8] <= 5.2865f) {
                if (features[8] <= 5.1156f) {
                    if (features[13] <= 40.6305f) {
                        return 12.3500f;
                    } else {
                        if (features[8] <= 4.4111f) {
                            if (features[6] <= 3.9312f) {
                                if (features[2] <= 45.9550f) {
                                    if (features[4] <= 0.0003f) {
                                        return 11.4125f;
                                    } else {
                                        return 11.4714f;
                                    }
                                } else {
                                    if (features[5] <= 0.0002f) {
                                        return 11.3625f;
                                    } else {
                                        return 11.3000f;
                                    }
                                }
                            } else {
                                return 11.0125f;
                            }
                        } else {
                            if (features[2] <= 49.6700f) {
                                if (features[12] <= 40.4195f) {
                                    return 11.7000f;
                                } else {
                                    if (features[5] <= 1.9682f) {
                                        return 11.5880f;
                                    } else {
                                        return 11.4857f;
                                    }
                                }
                            } else {
                                if (features[11] <= 6.4500f) {
                                    if (features[5] <= 0.0001f) {
                                        return 11.5000f;
                                    } else {
                                        return 11.5000f;
                                    }
                                } else {
                                    if (features[2] <= 49.9150f) {
                                        return 11.4900f;
                                    } else {
                                        return 11.4200f;
                                    }
                                }
                            }
                        }
                    }
                } else {
                    if (features[2] <= 48.2400f) {
                        if (features[8] <= 5.2225f) {
                            return 11.9118f;
                        } else {
                            if (features[4] <= -0.0009f) {
                                return 12.0556f;
                            } else {
                                return 11.9643f;
                            }
                        }
                    } else {
                        if (features[5] <= 0.0001f) {
                            return 11.8091f;
                        } else {
                            return 11.8000f;
                        }
                    }
                }
            } else {
                if (features[10] <= 12.5500f) {
                    if (features[2] <= 45.8000f) {
                        if (features[4] <= 0.2770f) {
                            if (features[8] <= 5.5182f) {
                                if (features[8] <= 5.4843f) {
                                    return 12.5308f;
                                } else {
                                    return 12.6000f;
                                }
                            } else {
                                if (features[7] <= 45.0441f) {
                                    return 12.6500f;
                                } else {
                                    return 12.6900f;
                                }
                            }
                        } else {
                            return 12.4455f;
                        }
                    } else {
                        if (features[12] <= 43.7079f) {
                            return 12.0200f;
                        } else {
                            if (features[8] <= 5.3625f) {
                                if (features[2] <= 46.9450f) {
                                    return 12.2000f;
                                } else {
                                    return 12.1200f;
                                }
                            } else {
                                if (features[2] <= 46.4250f) {
                                    return 12.3889f;
                                } else {
                                    return 12.2875f;
                                }
                            }
                        }
                    }
                } else {
                    if (features[13] <= 39.6334f) {
                        return 13.9500f;
                    } else {
                        return 13.2556f;
                    }
                }
            }
        }
    }
}

float predictETD_tree2(float features[14]) {
    if (features[8] <= 3.2690f) {
        if (features[8] <= 2.1664f) {
            if (features[2] <= 48.6850f) {
                if (features[2] <= 47.5350f) {
                    if (features[8] <= 2.1480f) {
                        if (features[4] <= 0.0017f) {
                            if (features[2] <= 47.1300f) {
                                return 8.9778f;
                            } else {
                                return 8.9000f;
                            }
                        } else {
                            return 8.8333f;
                        }
                    } else {
                        return 9.1071f;
                    }
                } else {
                    if (features[8] <= 2.0890f) {
                        if (features[8] <= 2.0758f) {
                            return 8.7100f;
                        } else {
                            return 8.7364f;
                        }
                    } else {
                        return 8.8000f;
                    }
                }
            } else {
                if (features[2] <= 49.5500f) {
                    if (features[8] <= 2.0298f) {
                        if (features[7] <= 49.2778f) {
                            return 8.5000f;
                        } else {
                            return 8.5818f;
                        }
                    } else {
                        if (features[8] <= 2.0419f) {
                            return 8.6000f;
                        } else {
                            return 8.6286f;
                        }
                    }
                } else {
                    if (features[7] <= 49.9127f) {
                        if (features[7] <= 49.5304f) {
                            return 8.4667f;
                        } else {
                            if (features[4] <= 0.0003f) {
                                if (features[5] <= 0.0002f) {
                                    if (features[4] <= -0.0003f) {
                                        return 8.4267f;
                                    } else {
                                        return 8.4500f;
                                    }
                                } else {
                                    if (features[8] <= 2.0026f) {
                                        return 8.4000f;
                                    } else {
                                        return 8.4167f;
                                    }
                                }
                            } else {
                                if (features[5] <= 0.0006f) {
                                    return 8.4000f;
                                } else {
                                    return 8.4250f;
                                }
                            }
                        }
                    } else {
                        return 8.5000f;
                    }
                }
            }
        } else {
            if (features[8] <= 3.0937f) {
                if (features[2] <= 41.1400f) {
                    if (features[4] <= 0.2175f) {
                        return 11.2400f;
                    } else {
                        return 10.2250f;
                    }
                } else {
                    if (features[8] <= 2.3066f) {
                        if (features[2] <= 45.5900f) {
                            if (features[5] <= 0.1324f) {
                                return 9.3214f;
                            } else {
                                return 9.2286f;
                            }
                        } else {
                            if (features[5] <= 0.0004f) {
                                if (features[2] <= 45.8350f) {
                                    return 9.2400f;
                                } else {
                                    return 9.2000f;
                                }
                            } else {
                                return 9.1667f;
                            }
                        }
                    } else {
                        if (features[2] <= 49.5800f) {
                            if (features[2] <= 48.7200f) {
                                if (features[4] <= 0.1232f) {
                                    return 9.7000f;
                                } else {
                                    return 9.6500f;
                                }
                            } else {
                                if (features[8] <= 3.0383f) {
                                    return 9.5667f;
                                } else {
                                    return 9.6000f;
                                }
                            }
                        } else {
                            if (features[11] <= 6.4500f) {
                                return 9.5000f;
                            } else {
                                if (features[8] <= 3.0063f) {
                                    if (features[4] <= -0.0015f) {
                                        return 9.4533f;
                                    } else {
                                        return 9.4121f;
                                    }
                                } else {
                                    return 9.5000f;
                                }
                            }
                        }
                    }
                }
            } else {
                if (features[8] <= 3.1649f) {
                    if (features[8] <= 3.1351f) {
                        if (features[8] <= 3.1188f) {
                            if (features[5] <= 0.0002f) {
                                return 9.7889f;
                            } else {
                                return 9.7500f;
                            }
                        } else {
                            if (features[4] <= -0.0006f) {
                                return 9.8000f;
                            } else {
                                return 9.8143f;
                            }
                        }
                    } else {
                        if (features[2] <= 47.5500f) {
                            return 9.9400f;
                        } else {
                            return 9.9000f;
                        }
                    }
                } else {
                    if (features[4] <= 0.1610f) {
                        if (features[2] <= 46.4550f) {
                            if (features[2] <= 46.1700f) {
                                return 10.2500f;
                            } else {
                                return 10.2000f;
                            }
                        } else {
                            if (features[2] <= 46.8500f) {
                                return 10.1000f;
                            } else {
                                if (features[4] <= -0.0009f) {
                                    return 10.0000f;
                                } else {
                                    return 10.0385f;
                                }
                            }
                        }
                    } else {
                        return 9.8875f;
                    }
                }
            }
        }
    } else {
        if (features[8] <= 4.2988f) {
            if (features[2] <= 40.9300f) {
                return 11.9375f;
            } else {
                if (features[8] <= 4.0746f) {
                    if (features[2] <= 42.7150f) {
                        return 10.8909f;
                    } else {
                        if (features[8] <= 3.4667f) {
                            if (features[2] <= 45.4400f) {
                                if (features[2] <= 45.0450f) {
                                    return 10.3625f;
                                } else {
                                    return 10.4273f;
                                }
                            } else {
                                if (features[10] <= 10.6500f) {
                                    return 10.3625f;
                                } else {
                                    return 10.3214f;
                                }
                            }
                        } else {
                            if (features[6] <= 2.6413f) {
                                if (features[8] <= 4.0044f) {
                                    if (features[5] <= 0.0007f) {
                                        return 10.4073f;
                                    } else {
                                        return 10.4222f;
                                    }
                                } else {
                                    if (features[4] <= -0.0028f) {
                                        return 10.4250f;
                                    } else {
                                        return 10.5200f;
                                    }
                                }
                            } else {
                                if (features[2] <= 49.9150f) {
                                    return 10.5875f;
                                } else {
                                    if (features[11] <= 6.4500f) {
                                        return 10.5000f;
                                    } else {
                                        return 10.4800f;
                                    }
                                }
                            }
                        }
                    }
                } else {
                    if (features[8] <= 4.2535f) {
                        if (features[12] <= 44.3006f) {
                            return 10.6455f;
                        } else {
                            if (features[2] <= 48.1250f) {
                                if (features[2] <= 47.5800f) {
                                    return 11.0462f;
                                } else {
                                    if (features[4] <= 0.0009f) {
                                        return 10.9000f;
                                    } else {
                                        return 10.9200f;
                                    }
                                }
                            } else {
                                if (features[8] <= 4.1169f) {
                                    return 10.7000f;
                                } else {
                                    return 10.8000f;
                                }
                            }
                        }
                    } else {
                        if (features[7] <= 46.0872f) {
                            return 10.9571f;
                        } else {
                            return 11.1714f;
                        }
                    }
                }
            }
        } else {
            if (features[8] <= 5.3084f) {
                if (features[13] <= 40.6305f) {
                    return 12.5625f;
                } else {
                    if (features[8] <= 5.1240f) {
                        if (features[8] <= 4.4039f) {
                            if (features[4] <= 0.0023f) {
                                if (features[8] <= 4.3360f) {
                                    return 11.2333f;
                                } else {
                                    if (features[2] <= 45.6950f) {
                                        return 11.4667f;
                                    } else {
                                        return 11.3923f;
                                    }
                                }
                            } else {
                                return 11.1600f;
                            }
                        } else {
                            if (features[2] <= 49.5600f) {
                                if (features[8] <= 5.0782f) {
                                    if (features[5] <= 4.9588f) {
                                        return 11.5679f;
                                    } else {
                                        return 11.4625f;
                                    }
                                } else {
                                    return 11.6727f;
                                }
                            } else {
                                if (features[6] <= 2.6413f) {
                                    if (features[2] <= 49.9250f) {
                                        return 11.5000f;
                                    } else {
                                        return 11.4162f;
                                    }
                                } else {
                                    if (features[13] <= 50.0805f) {
                                        return 11.4650f;
                                    } else {
                                        return 11.5000f;
                                    }
                                }
                            }
                        }
                    } else {
                        if (features[2] <= 48.0700f) {
                            if (features[8] <= 5.2687f) {
                                if (features[2] <= 47.8600f) {
                                    if (features[5] <= 0.0003f) {
                                        return 11.9667f;
                                    } else {
                                        return 12.0000f;
                                    }
                                } else {
                                    return 11.9308f;
                                }
                            } else {
                                return 12.0917f;
                            }
                        } else {
                            if (features[2] <= 48.4500f) {
                                return 11.8500f;
                            } else {
                                return 11.8000f;
                            }
                        }
                    }
                }
            } else {
                if (features[2] <= 41.6550f) {
                    if (features[11] <= 8.5500f) {
                        return 13.6250f;
                    } else {
                        return 14.3727f;
                    }
                } else {
                    if (features[2] <= 45.4250f) {
                        if (features[10] <= 12.4500f) {
                            if (features[2] <= 44.9650f) {
                                return 12.5000f;
                            } else {
                                if (features[8] <= 5.5389f) {
                                    return 12.6333f;
                                } else {
                                    return 12.7000f;
                                }
                            }
                        } else {
                            return 12.9600f;
                        }
                    } else {
                        if (features[7] <= 44.7718f) {
                            return 12.0000f;
                        } else {
                            if (features[8] <= 5.4189f) {
                                if (features[2] <= 46.6200f) {
                                    if (features[7] <= 46.4449f) {
                                        return 12.3000f;
                                    } else {
                                        return 12.3636f;
                                    }
                                } else {
                                    return 12.2083f;
                                }
                            } else {
                                if (features[8] <= 5.4675f) {
                                    return 12.4375f;
                                } else {
                                    return 12.5182f;
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

float predictETD_tree3(float features[14]) {
    if (features[8] <= 3.2690f) {
        if (features[8] <= 2.1466f) {
            if (features[8] <= 2.0561f) {
                if (features[8] <= 2.0182f) {
                    if (features[6] <= 2.6413f) {
                        if (features[2] <= 49.9250f) {
                            return 8.4273f;
                        } else {
                            if (features[5] <= 0.0009f) {
                                if (features[5] <= 0.0001f) {
                                    return 8.4125f;
                                } else {
                                    return 8.4000f;
                                }
                            } else {
                                return 8.4167f;
                            }
                        }
                    } else {
                        if (features[7] <= 49.7852f) {
                            if (features[2] <= 49.9750f) {
                                return 8.4222f;
                            } else {
                                return 8.4800f;
                            }
                        } else {
                            return 8.5000f;
                        }
                    }
                } else {
                    if (features[2] <= 49.2650f) {
                        if (features[4] <= -0.0009f) {
                            return 8.6222f;
                        } else {
                            if (features[8] <= 2.0387f) {
                                return 8.6000f;
                            } else {
                                return 8.5800f;
                            }
                        }
                    } else {
                        return 8.5600f;
                    }
                }
            } else {
                if (features[8] <= 2.1193f) {
                    if (features[2] <= 47.8700f) {
                        if (features[4] <= 0.0006f) {
                            return 8.8625f;
                        } else {
                            return 8.7714f;
                        }
                    } else {
                        if (features[6] <= 2.8063f) {
                            if (features[4] <= 0.0003f) {
                                return 8.7000f;
                            } else {
                                return 8.7000f;
                            }
                        } else {
                            return 8.7375f;
                        }
                    }
                } else {
                    if (features[5] <= 0.0005f) {
                        return 8.9750f;
                    } else {
                        return 8.9167f;
                    }
                }
            }
        } else {
            if (features[8] <= 3.0937f) {
                if (features[2] <= 40.9600f) {
                    return 10.5643f;
                } else {
                    if (features[8] <= 2.3037f) {
                        if (features[8] <= 2.1690f) {
                            if (features[8] <= 2.1617f) {
                                return 9.1000f;
                            } else {
                                return 9.1143f;
                            }
                        } else {
                            if (features[4] <= 0.0014f) {
                                if (features[2] <= 45.4850f) {
                                    if (features[2] <= 45.1550f) {
                                        return 9.3667f;
                                    } else {
                                        return 9.3143f;
                                    }
                                } else {
                                    if (features[8] <= 2.1827f) {
                                        return 9.2000f;
                                    } else {
                                        return 9.2545f;
                                    }
                                }
                            } else {
                                if (features[4] <= 0.3213f) {
                                    return 9.2333f;
                                } else {
                                    return 9.1750f;
                                }
                            }
                        }
                    } else {
                        if (features[2] <= 49.6000f) {
                            if (features[2] <= 48.9900f) {
                                if (features[4] <= 0.2621f) {
                                    return 9.7000f;
                                } else {
                                    return 9.6286f;
                                }
                            } else {
                                return 9.5882f;
                            }
                        } else {
                            if (features[13] <= 50.0805f) {
                                if (features[8] <= 3.0063f) {
                                    if (features[4] <= -0.0015f) {
                                        return 9.4400f;
                                    } else {
                                        return 9.4112f;
                                    }
                                } else {
                                    return 9.5000f;
                                }
                            } else {
                                return 9.5000f;
                            }
                        }
                    }
                }
            } else {
                if (features[2] <= 47.3950f) {
                    if (features[2] <= 46.4600f) {
                        if (features[4] <= -0.0009f) {
                            return 10.2300f;
                        } else {
                            return 10.1800f;
                        }
                    } else {
                        if (features[2] <= 46.7150f) {
                            return 10.1000f;
                        } else {
                            if (features[2] <= 46.9350f) {
                                return 9.9333f;
                            } else {
                                if (features[2] <= 47.1050f) {
                                    return 10.0417f;
                                } else {
                                    return 10.0000f;
                                }
                            }
                        }
                    }
                } else {
                    if (features[2] <= 47.8900f) {
                        if (features[2] <= 47.7300f) {
                            return 9.9083f;
                        } else {
                            return 9.8727f;
                        }
                    } else {
                        if (features[8] <= 3.1153f) {
                            if (features[8] <= 3.1040f) {
                                return 9.7778f;
                            } else {
                                return 9.7400f;
                            }
                        } else {
                            return 9.8000f;
                        }
                    }
                }
            }
        }
    } else {
        if (features[8] <= 4.3192f) {
            if (features[11] <= 8.1500f) {
                if (features[8] <= 4.0825f) {
                    if (features[2] <= 42.7150f) {
                        return 10.8700f;
                    } else {
                        if (features[8] <= 4.0352f) {
                            if (features[7] <= 49.9127f) {
                                if (features[8] <= 3.3058f) {
                                    if (features[4] <= 0.0003f) {
                                        return 10.3571f;
                                    } else {
                                        return 10.3000f;
                                    }
                                } else {
                                    if (features[6] <= 3.3312f) {
                                        return 10.4124f;
                                    } else {
                                        return 10.4846f;
                                    }
                                }
                            } else {
                                return 10.5000f;
                            }
                        } else {
                            return 10.6214f;
                        }
                    }
                } else {
                    if (features[8] <= 4.2544f) {
                        if (features[11] <= 6.9000f) {
                            if (features[2] <= 48.0150f) {
                                if (features[10] <= 10.1500f) {
                                    return 10.9000f;
                                } else {
                                    if (features[2] <= 47.6700f) {
                                        return 10.9857f;
                                    } else {
                                        return 10.9500f;
                                    }
                                }
                            } else {
                                if (features[2] <= 48.5950f) {
                                    return 10.8067f;
                                } else {
                                    return 10.7000f;
                                }
                            }
                        } else {
                            return 10.6600f;
                        }
                    } else {
                        if (features[4] <= 0.0020f) {
                            return 11.1882f;
                        } else {
                            return 10.9750f;
                        }
                    }
                }
            } else {
                return 11.6867f;
            }
        } else {
            if (features[8] <= 5.3254f) {
                if (features[8] <= 5.1077f) {
                    if (features[2] <= 42.0900f) {
                        return 12.2667f;
                    } else {
                        if (features[13] <= 43.3577f) {
                            return 11.7222f;
                        } else {
                            if (features[8] <= 4.4082f) {
                                if (features[6] <= 3.1513f) {
                                    if (features[4] <= -0.0003f) {
                                        return 11.3727f;
                                    } else {
                                        return 11.4375f;
                                    }
                                } else {
                                    if (features[5] <= 0.0004f) {
                                        return 11.3417f;
                                    } else {
                                        return 11.2000f;
                                    }
                                }
                            } else {
                                if (features[6] <= 2.6413f) {
                                    if (features[2] <= 49.8500f) {
                                        return 11.5333f;
                                    } else {
                                        return 11.4247f;
                                    }
                                } else {
                                    if (features[8] <= 5.0424f) {
                                        return 11.5019f;
                                    } else {
                                        return 11.6000f;
                                    }
                                }
                            }
                        }
                    }
                } else {
                    if (features[2] <= 47.2950f) {
                        if (features[2] <= 47.1250f) {
                            return 12.4000f;
                        } else {
                            return 12.1000f;
                        }
                    } else {
                        if (features[2] <= 48.2400f) {
                            if (features[4] <= 0.0018f) {
                                if (features[2] <= 47.8350f) {
                                    return 11.9812f;
                                } else {
                                    return 11.9067f;
                                }
                            } else {
                                return 11.8333f;
                            }
                        } else {
                            if (features[2] <= 48.3550f) {
                                return 11.8167f;
                            } else {
                                return 11.7909f;
                            }
                        }
                    }
                }
            } else {
                if (features[2] <= 41.6550f) {
                    if (features[2] <= 39.7100f) {
                        return 14.2667f;
                    } else {
                        return 13.4750f;
                    }
                } else {
                    if (features[2] <= 45.4700f) {
                        if (features[8] <= 5.8625f) {
                            if (features[5] <= 0.0002f) {
                                return 12.6778f;
                            } else {
                                if (features[13] <= 44.2549f) {
                                    return 12.6000f;
                                } else {
                                    return 12.6200f;
                                }
                            }
                        } else {
                            return 12.9833f;
                        }
                    } else {
                        if (features[10] <= 11.2000f) {
                            if (features[2] <= 46.4250f) {
                                if (features[8] <= 5.4484f) {
                                    if (features[6] <= 3.1513f) {
                                        return 12.3667f;
                                    } else {
                                        return 12.3889f;
                                    }
                                } else {
                                    return 12.5000f;
                                }
                            } else {
                                if (features[8] <= 5.3625f) {
                                    return 12.2375f;
                                } else {
                                    return 12.2833f;
                                }
                            }
                        } else {
                            return 11.9667f;
                        }
                    }
                }
            }
        }
    }
}

float predictETD_tree4(float features[14]) {
    if (features[8] <= 3.2866f) {
        if (features[8] <= 2.1683f) {
            if (features[8] <= 2.0570f) {
                if (features[2] <= 49.6450f) {
                    if (features[4] <= 0.0027f) {
                        if (features[2] <= 49.2500f) {
                            if (features[8] <= 2.0398f) {
                                return 8.6000f;
                            } else {
                                return 8.6111f;
                            }
                        } else {
                            return 8.5583f;
                        }
                    } else {
                        return 8.5200f;
                    }
                } else {
                    if (features[11] <= 6.4500f) {
                        return 8.5000f;
                    } else {
                        if (features[4] <= 0.1915f) {
                            if (features[4] <= -0.0012f) {
                                if (features[8] <= 2.0014f) {
                                    return 8.4636f;
                                } else {
                                    return 8.4067f;
                                }
                            } else {
                                if (features[5] <= 0.0008f) {
                                    if (features[8] <= 2.0014f) {
                                        return 8.4000f;
                                    } else {
                                        return 8.4080f;
                                    }
                                } else {
                                    return 8.4235f;
                                }
                            }
                        } else {
                            return 8.4667f;
                        }
                    }
                }
            } else {
                if (features[8] <= 2.1227f) {
                    if (features[2] <= 47.8700f) {
                        if (features[6] <= 2.9763f) {
                            return 8.8500f;
                        } else {
                            return 8.7778f;
                        }
                    } else {
                        if (features[8] <= 2.0706f) {
                            return 8.7000f;
                        } else {
                            return 8.7600f;
                        }
                    }
                } else {
                    if (features[12] <= 46.8610f) {
                        if (features[5] <= 0.0001f) {
                            return 9.0800f;
                        } else {
                            return 9.1000f;
                        }
                    } else {
                        return 8.9875f;
                    }
                }
            }
        } else {
            if (features[11] <= 8.2000f) {
                if (features[8] <= 3.1005f) {
                    if (features[8] <= 2.3005f) {
                        if (features[4] <= 0.0017f) {
                            if (features[2] <= 45.6400f) {
                                return 9.3167f;
                            } else {
                                return 9.2385f;
                            }
                        } else {
                            return 9.1917f;
                        }
                    } else {
                        if (features[2] <= 49.4750f) {
                            if (features[11] <= 7.7500f) {
                                if (features[5] <= 1.9179f) {
                                    if (features[2] <= 48.7550f) {
                                        return 9.7071f;
                                    } else {
                                        return 9.6133f;
                                    }
                                } else {
                                    return 9.5000f;
                                }
                            } else {
                                return 9.8667f;
                            }
                        } else {
                            if (features[13] <= 50.0805f) {
                                if (features[2] <= 49.9000f) {
                                    if (features[7] <= 49.5304f) {
                                        return 9.5000f;
                                    } else {
                                        return 9.5444f;
                                    }
                                } else {
                                    if (features[4] <= -0.0015f) {
                                        return 9.4500f;
                                    } else {
                                        return 9.4122f;
                                    }
                                }
                            } else {
                                return 9.5000f;
                            }
                        }
                    }
                } else {
                    if (features[8] <= 3.1649f) {
                        if (features[8] <= 3.1397f) {
                            if (features[6] <= 2.8063f) {
                                if (features[5] <= 0.0004f) {
                                    return 9.8000f;
                                } else {
                                    return 9.7900f;
                                }
                            } else {
                                return 9.7400f;
                            }
                        } else {
                            return 9.9125f;
                        }
                    } else {
                        if (features[2] <= 46.2600f) {
                            if (features[8] <= 3.2595f) {
                                return 10.2182f;
                            } else {
                                return 10.2692f;
                            }
                        } else {
                            if (features[2] <= 47.0000f) {
                                if (features[5] <= 0.0019f) {
                                    if (features[8] <= 3.2055f) {
                                        return 10.0875f;
                                    } else {
                                        return 10.1056f;
                                    }
                                } else {
                                    return 10.0182f;
                                }
                            } else {
                                if (features[5] <= 0.0002f) {
                                    return 10.0286f;
                                } else {
                                    return 10.0000f;
                                }
                            }
                        }
                    }
                }
            } else {
                return 11.6111f;
            }
        }
    } else {
        if (features[8] <= 5.1108f) {
            if (features[8] <= 4.1625f) {
                if (features[2] <= 42.3750f) {
                    return 11.1421f;
                } else {
                    if (features[8] <= 4.0783f) {
                        if (features[8] <= 4.0323f) {
                            if (features[7] <= 49.9127f) {
                                if (features[4] <= 0.3182f) {
                                    if (features[8] <= 4.0060f) {
                                        return 10.4086f;
                                    } else {
                                        return 10.4800f;
                                    }
                                } else {
                                    return 10.5182f;
                                }
                            } else {
                                if (features[8] <= 4.0012f) {
                                    return 10.5000f;
                                } else {
                                    return 10.5000f;
                                }
                            }
                        } else {
                            return 10.5900f;
                        }
                    } else {
                        if (features[8] <= 4.1293f) {
                            return 10.7143f;
                        } else {
                            return 10.8091f;
                        }
                    }
                }
            } else {
                if (features[11] <= 7.9500f) {
                    if (features[8] <= 4.3497f) {
                        if (features[2] <= 47.0200f) {
                            if (features[6] <= 3.4250f) {
                                if (features[2] <= 46.3300f) {
                                    return 11.3375f;
                                } else {
                                    if (features[8] <= 4.2662f) {
                                        return 11.1143f;
                                    } else {
                                        return 11.2000f;
                                    }
                                }
                            } else {
                                return 11.0667f;
                            }
                        } else {
                            if (features[5] <= 2.9882f) {
                                if (features[8] <= 4.2030f) {
                                    return 10.9100f;
                                } else {
                                    return 11.0000f;
                                }
                            } else {
                                return 10.7375f;
                            }
                        }
                    } else {
                        if (features[8] <= 4.4068f) {
                            if (features[4] <= 0.0017f) {
                                if (features[2] <= 45.6350f) {
                                    return 11.4667f;
                                } else {
                                    return 11.3857f;
                                }
                            } else {
                                return 11.0625f;
                            }
                        } else {
                            if (features[2] <= 49.6700f) {
                                if (features[7] <= 41.3509f) {
                                    return 11.7286f;
                                } else {
                                    if (features[12] <= 44.7014f) {
                                        return 11.4143f;
                                    } else {
                                        return 11.5684f;
                                    }
                                }
                            } else {
                                if (features[13] <= 50.0805f) {
                                    if (features[8] <= 5.0075f) {
                                        return 11.4227f;
                                    } else {
                                        return 11.4826f;
                                    }
                                } else {
                                    return 11.5000f;
                                }
                            }
                        }
                    }
                } else {
                    return 12.3667f;
                }
            }
        } else {
            if (features[2] <= 42.0550f) {
                if (features[13] <= 37.7791f) {
                    return 14.2214f;
                } else {
                    if (features[8] <= 6.0772f) {
                        return 13.1167f;
                    } else {
                        return 13.6333f;
                    }
                }
            } else {
                if (features[2] <= 45.9400f) {
                    if (features[8] <= 5.7519f) {
                        if (features[11] <= 7.2500f) {
                            if (features[8] <= 5.4867f) {
                                if (features[8] <= 5.4573f) {
                                    return 12.4400f;
                                } else {
                                    if (features[6] <= 3.1513f) {
                                        return 12.5000f;
                                    } else {
                                        return 12.5125f;
                                    }
                                }
                            } else {
                                if (features[2] <= 45.3050f) {
                                    return 12.6500f;
                                } else {
                                    return 12.6000f;
                                }
                            }
                        } else {
                            return 12.3727f;
                        }
                    } else {
                        return 12.8250f;
                    }
                } else {
                    if (features[2] <= 47.2900f) {
                        if (features[5] <= 0.0007f) {
                            if (features[8] <= 5.3573f) {
                                if (features[8] <= 5.3254f) {
                                    return 12.1091f;
                                } else {
                                    return 12.2111f;
                                }
                            } else {
                                if (features[2] <= 46.4250f) {
                                    return 12.3667f;
                                } else {
                                    return 12.3000f;
                                }
                            }
                        } else {
                            return 12.0545f;
                        }
                    } else {
                        if (features[2] <= 48.1400f) {
                            if (features[5] <= 0.0012f) {
                                if (features[8] <= 5.2236f) {
                                    return 11.9200f;
                                } else {
                                    if (features[8] <= 5.2444f) {
                                        return 11.9875f;
                                    } else {
                                        return 12.0083f;
                                    }
                                }
                            } else {
                                return 11.8375f;
                            }
                        } else {
                            if (features[8] <= 5.1536f) {
                                return 11.7667f;
                            } else {
                                return 11.8200f;
                            }
                        }
                    }
                }
            }
        }
    }
}

float predictETD(float features[14]) {
    float sum = 0.0f;
    sum += predictETD_tree0(features);
    sum += predictETD_tree1(features);
    sum += predictETD_tree2(features);
    sum += predictETD_tree3(features);
    sum += predictETD_tree4(features);
    return sum / 5.0f;
}

#endif
