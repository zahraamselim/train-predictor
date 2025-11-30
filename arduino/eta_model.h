#ifndef ETA_MODEL_H
#define ETA_MODEL_H

float predictETA(float features[6]) {
    if (features[1] <= 65.500f) {
        if (features[1] <= 34.100f) {
            if (features[3] <= 112.479f) {
                if (features[3] <= 99.185f) {
                    if (features[1] <= 31.700f) {
                        if (features[1] <= 30.350f) {
                            if (features[1] <= 29.950f) {
                                return 29.700;
                            } else {
                                return 30.186;
                            }
                        } else {
                            if (features[3] <= 94.754f) {
                                return 31.175;
                            } else {
                                return 30.560;
                            }
                        }
                    } else {
                        if (features[3] <= 88.432f) {
                            if (features[1] <= 33.725f) {
                                return 33.293;
                            } else {
                                return 33.987;
                            }
                        } else {
                            if (features[3] <= 90.209f) {
                                return 32.679;
                            } else {
                                return 32.025;
                            }
                        }
                    }
                } else {
                    if (features[1] <= 27.700f) {
                        if (features[1] <= 26.875f) {
                            if (features[3] <= 110.246f) {
                                return 26.717;
                            } else {
                                return 26.244;
                            }
                        } else {
                            if (features[3] <= 106.911f) {
                                return 27.487;
                            } else {
                                return 27.172;
                            }
                        }
                    } else {
                        if (features[3] <= 102.137f) {
                            if (features[3] <= 100.813f) {
                                return 29.240;
                            } else {
                                return 28.750;
                            }
                        } else {
                            if (features[3] <= 104.052f) {
                                return 28.403;
                            } else {
                                return 27.862;
                            }
                        }
                    }
                }
            } else {
                if (features[1] <= 22.375f) {
                    if (features[3] <= 144.184f) {
                        if (features[1] <= 21.325f) {
                            if (features[1] <= 20.650f) {
                                return 20.500;
                            } else {
                                return 20.992;
                            }
                        } else {
                            if (features[3] <= 133.304f) {
                                return 22.181;
                            } else {
                                return 21.608;
                            }
                        }
                    } else {
                        if (features[3] <= 152.079f) {
                            if (features[3] <= 148.968f) {
                                return 19.858;
                            } else {
                                return 19.462;
                            }
                        } else {
                            if (features[1] <= 18.775f) {
                                return 18.483;
                            } else {
                                return 19.025;
                            }
                        }
                    }
                } else {
                    if (features[3] <= 121.374f) {
                        if (features[3] <= 116.991f) {
                            if (features[3] <= 115.030f) {
                                return 25.650;
                            } else {
                                return 25.205;
                            }
                        } else {
                            if (features[3] <= 119.021f) {
                                return 24.781;
                            } else {
                                return 24.285;
                            }
                        }
                    } else {
                        if (features[1] <= 23.175f) {
                            if (features[1] <= 22.725f) {
                                return 22.567;
                            } else {
                                return 23.056;
                            }
                        } else {
                            if (features[1] <= 23.575f) {
                                return 23.380;
                            } else {
                                return 23.844;
                            }
                        }
                    }
                }
            }
        } else {
            if (features[3] <= 62.110f) {
                if (features[1] <= 54.850f) {
                    if (features[1] <= 50.525f) {
                        if (features[1] <= 48.625f) {
                            if (features[1] <= 47.550f) {
                                return 47.233;
                            } else {
                                return 48.200;
                            }
                        } else {
                            if (features[1] <= 49.650f) {
                                return 49.125;
                            } else {
                                return 50.000;
                            }
                        }
                    } else {
                        if (features[1] <= 52.725f) {
                            if (features[3] <= 56.595f) {
                                return 52.050;
                            } else {
                                return 51.183;
                            }
                        } else {
                            if (features[3] <= 53.979f) {
                                return 54.500;
                            } else {
                                return 53.300;
                            }
                        }
                    }
                } else {
                    if (features[1] <= 60.200f) {
                        if (features[3] <= 50.913f) {
                            if (features[3] <= 49.847f) {
                                return 59.250;
                            } else {
                                return 57.983;
                            }
                        } else {
                            if (features[3] <= 52.426f) {
                                return 56.500;
                            } else {
                                return 55.200;
                            }
                        }
                    } else {
                        if (features[3] <= 45.754f) {
                            return 64.800;
                        } else {
                            if (features[3] <= 47.301f) {
                                return 62.400;
                            } else {
                                return 60.983;
                            }
                        }
                    }
                }
            } else {
                if (features[1] <= 40.025f) {
                    if (features[3] <= 78.388f) {
                        if (features[1] <= 38.425f) {
                            if (features[3] <= 77.143f) {
                                return 38.083;
                            } else {
                                return 37.550;
                            }
                        } else {
                            if (features[3] <= 74.341f) {
                                return 39.460;
                            } else {
                                return 38.850;
                            }
                        }
                    } else {
                        if (features[1] <= 35.650f) {
                            if (features[3] <= 83.975f) {
                                return 35.117;
                            } else {
                                return 34.450;
                            }
                        } else {
                            if (features[1] <= 36.675f) {
                                return 36.459;
                            } else {
                                return 36.925;
                            }
                        }
                    }
                } else {
                    if (features[1] <= 43.425f) {
                        if (features[3] <= 70.143f) {
                            if (features[0] <= 56.600f) {
                                return 42.120;
                            } else {
                                return 42.956;
                            }
                        } else {
                            if (features[3] <= 71.341f) {
                                return 41.133;
                            } else {
                                return 40.517;
                            }
                        }
                    } else {
                        if (features[3] <= 64.621f) {
                            if (features[1] <= 45.950f) {
                                return 45.450;
                            } else {
                                return 46.375;
                            }
                        } else {
                            if (features[3] <= 65.455f) {
                                return 44.920;
                            } else {
                                return 44.111;
                            }
                        }
                    }
                }
            }
        }
    } else {
        if (features[1] <= 96.900f) {
            if (features[3] <= 37.440f) {
                if (features[3] <= 32.764f) {
                    if (features[1] <= 94.250f) {
                        if (features[1] <= 93.225f) {
                            return 92.800;
                        } else {
                            return 93.650;
                        }
                    } else {
                        return 94.850;
                    }
                } else {
                    if (features[0] <= 77.550f) {
                        if (features[1] <= 83.825f) {
                            return 83.600;
                        } else {
                            return 84.050;
                        }
                    } else {
                        return 85.500;
                    }
                }
            } else {
                if (features[1] <= 68.350f) {
                    if (features[3] <= 43.982f) {
                        return 66.400;
                    } else {
                        return 66.200;
                    }
                } else {
                    if (features[3] <= 41.018f) {
                        if (features[4] <= -0.179f) {
                            if (features[3] <= 40.500f) {
                                return 72.100;
                            } else {
                                return 71.900;
                            }
                        } else {
                            if (features[4] <= -0.106f) {
                                return 72.550;
                            } else {
                                return 72.900;
                            }
                        }
                    } else {
                        return 70.300;
                    }
                }
            }
        } else {
            if (features[1] <= 118.775f) {
                if (features[1] <= 104.375f) {
                    if (features[1] <= 101.000f) {
                        if (features[0] <= 104.025f) {
                            return 99.600;
                        } else {
                            return 98.950;
                        }
                    } else {
                        return 102.400;
                    }
                } else {
                    if (features[1] <= 113.275f) {
                        if (features[1] <= 108.200f) {
                            if (features[2] <= 41.889f) {
                                return 106.400;
                            } else {
                                return 107.200;
                            }
                        } else {
                            if (features[1] <= 109.925f) {
                                return 109.200;
                            } else {
                                return 111.075;
                            }
                        }
                    } else {
                        if (features[2] <= 32.708f) {
                            return 115.350;
                        } else {
                            return 115.050;
                        }
                    }
                }
            } else {
                if (features[3] <= 23.235f) {
                    if (features[4] <= -0.052f) {
                        return 129.350;
                    } else {
                        if (features[0] <= 135.475f) {
                            return 127.300;
                        } else {
                            return 128.000;
                        }
                    }
                } else {
                    if (features[2] <= 39.410f) {
                        return 122.200;
                    } else {
                        if (features[3] <= 23.607f) {
                            return 123.750;
                        } else {
                            return 123.300;
                        }
                    }
                }
            }
        }
    }
}

#endif
